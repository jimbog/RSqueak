from rpython.rlib import jit

from rsqueakvm import constants
from rsqueakvm.error import FatalError, WrapperException, PrimitiveFailedError
from rsqueakvm.model.display import W_DisplayBitmap, from_words_object
from rsqueakvm.model.pointers import W_PointersObject


class Wrapper(object):
    def __init__(self, space, w_self):
        if not isinstance(w_self, W_PointersObject):
            raise WrapperException("Unexpected instance given to wrapper")
        self.wrapped = w_self
        self.space = space

    def read(self, index0):
        try:
            return self.wrapped.fetch(self.space, index0)
            # XXX Index error never raised after translation
        except IndexError:
            raise WrapperException("Unexpected instance layout. Too small")

    def write(self, index0, w_new):
        try:
            self.wrapped.store(self.space, index0, w_new)
            # XXX Index error never raised after translation
        except IndexError:
            raise WrapperException("Unexpected instance layout. Too small")

class VarsizedWrapper(Wrapper):
    def at0(self, i0):
        return self.wrapped.at0(self.space, i0)

    def atput0(self, i0, w_value):
        return self.wrapped.atput0(self.space, i0, w_value)

def make_getter(index0):
    def getter(self):
        return self.read(index0)
    return getter

def make_setter(index0):
    def setter(self, w_new):
        return self.write(index0, w_new)
    return setter

def make_getter_setter(index0):
    return make_getter(index0), make_setter(index0)

def make_int_getter(index0):
    def getter(self):
        return self.space.unwrap_int(self.read(index0))
    return getter

def make_int_setter(index0):
    def setter(self, new):
        return self.write(index0, self.space.wrap_int(new))
    return setter

def make_int_getter_setter(index0):
    return make_int_getter(index0), make_int_setter(index0)


class LinkWrapper(Wrapper):
    next_link, store_next_link = make_getter_setter(0)

class ProcessWrapper(LinkWrapper):
    suspended_context, store_suspended_context = make_getter_setter(1)
    priority = make_int_getter(2)
    my_list, store_my_list = make_getter_setter(3)

    def put_to_sleep(self):
        sched = scheduler(self.space)
        priority = self.priority()
        process_list = sched.get_process_list(priority)
        process_list.add_last_link(self.wrapped)

    def transfer_to_self_from(self, s_old_frame, forced=False):
        from rsqueakvm.interpreter import ProcessSwitch
        assert not self.is_active_process(), "trying to switch to already active process"
        new_proc = self.wrapped
        sched = scheduler(self.space)
        old_proc = ProcessWrapper(self.space, sched.active_process())
        sched.store_active_process(new_proc)
        self.store_my_list(self.space.w_nil)
        old_proc.store_suspended_context(s_old_frame.w_self())
        w_new_active_context = self.suspended_context()
        self.store_suspended_context(self.space.w_nil)
        assert isinstance(w_new_active_context, W_PointersObject)
        raise ProcessSwitch(w_new_active_context.as_context_get_shadow(self.space), forced=forced)

    def resume(self, s_current_frame, forced=False):
        sched = scheduler(self.space)
        active_process = ProcessWrapper(self.space, sched.active_process())
        active_priority = active_process.priority()
        priority = self.priority()
        if priority > active_priority:
            if not self.space.suppress_process_switch.is_set():
                active_process.put_to_sleep()
                self.transfer_to_self_from(s_current_frame, forced=forced)
        else:
            self.put_to_sleep()

    def is_active_process(self):
        return self.wrapped.is_same_object(scheduler(self.space).active_process())

    def suspend(self, s_current_frame):
        if self.is_active_process():
            if not self.space.suppress_process_switch.is_set():
                new_proc = scheduler(self.space).wake_highest_priority_process()
                new_proc.transfer_to_self_from(s_current_frame)
        else:
            w_my_list = self.my_list()
            if self.my_list().is_nil(self.space):
                raise PrimitiveFailedError
            process_list = LinkedListWrapper(self.space, self.my_list())
            process_list.remove(self.wrapped)
            self.store_my_list(self.space.w_nil)

    def yield_(self, s_current_frame):
        sched = scheduler(self.space)
        w_active_proc = sched.active_process()
        priority = ProcessWrapper(self.space, w_active_proc).priority()
        process_list = sched.get_process_list(priority)
        if not process_list.is_empty_list():
            process_list.add_last_link(w_active_proc)
            sched.wake_highest_priority_process().transfer_to_self_from(s_current_frame)

class LinkedListWrapper(Wrapper):
    first_link, store_first_link = make_getter_setter(0)
    last_link, store_last_link = make_getter_setter(1)

    def is_empty_list(self):
        return self.first_link().is_nil(self.space)

    def add_last_link(self, w_process):
        if self.is_empty_list():
            self.store_first_link(w_process)
        else:
            last_link = LinkWrapper(self.space, self.last_link())
            last_link.store_next_link(w_process)
        self.store_last_link(w_process)
        ProcessWrapper(self.space, w_process).store_my_list(self.wrapped)

    def remove_first_link_of_list(self):
        w_first = self.first_link()
        w_last = self.last_link()
        if w_first.is_same_object(w_last):
            self.store_first_link(self.space.w_nil)
            self.store_last_link(self.space.w_nil)
        else:
            w_next = LinkWrapper(self.space, w_first).next_link()
            self.store_first_link(w_next)
        LinkWrapper(self.space, w_first).store_next_link(self.space.w_nil)
        return w_first

    def remove(self, w_link):
        # It is perfectly fine that this does not fail if the w_link is not in
        # the list. That just means we ran suspend more than once, for example,
        # or we are waiting on something and called suspend. Both things are
        # fine.
        if self.first_link().is_same_object(w_link):
            self.remove_first_link_of_list()
        elif self.first_link().is_nil(self.space):
            return
        else:
            current = LinkWrapper(self.space, self.first_link())
            w_next = current.next_link()
            while not w_next.is_nil(self.space):
                if w_next.is_same_object(w_link):
                    LinkWrapper(self.space, w_link).store_next_link(self.space.w_nil)
                    w_tail = LinkWrapper(self.space, w_next).next_link()
                    current.store_next_link(w_tail)
                    if w_tail.is_nil(self.space):
                        self.store_last_link(current.wrapped)
                    return
                current = LinkWrapper(self.space, w_next)
                w_next = current.next_link()

class AssociationWrapper(Wrapper):
    key = make_getter(0)
    value, store_value = make_getter_setter(1)

    @staticmethod
    def build(space, w_assoc):
        if w_assoc.getclass(space).is_same_object(space.w_ClassBinding):
            return PromotingAssociationWrapper(space, w_assoc)
        else:
            return AssociationWrapper(space, w_assoc)

    @staticmethod
    def make_w_assoc(space, w_key, w_value):
        w_association = space.w_schedulerassociationpointer
        w_association_class = w_association.getclass(space)
        w_new_association = w_association_class.as_class_get_shadow(space).new()
        w_new_association.store(space, 0, w_key)
        w_new_association.store(space, 1, w_value)
        return w_new_association

class PromotingAssociationWrapper(AssociationWrapper):
    def value(self):
        return jit.promote(self.read(1))

class SchedulerWrapper(Wrapper):
    active_process, store_active_process = make_getter_setter(1)

    def priority_list(self):
        return self.read(0)

    def process_list(self, priority):
        # priority is 1-indexed, we read with 0-indexed
        return self.priority_list().fetch(self.space, priority - 1)

    def get_process_list(self, priority):
        return LinkedListWrapper(self.space, self.process_list(priority))

    def wake_highest_priority_process(self):
        w_lists = self.priority_list()
        return ProcessWrapper(self.space, unwrapped_wake_highest_priority_process(self.space, w_lists))

def unwrapped_wake_highest_priority_process(space, w_lists):
    for i in range(w_lists.size() - 1, -1, -1):
        process_list = LinkedListWrapper(space, w_lists.fetch(space, i))
        if not process_list.is_empty_list():
            return process_list.remove_first_link_of_list()
    raise FatalError("Scheduler could not find a runnable process")

def scheduler(space):
    return SchedulerWrapper(space, space.w_Processor)

class SemaphoreWrapper(LinkedListWrapper):
    excess_signals, store_excess_signals = make_int_getter_setter(2)

    def signal(self, s_current_frame, forced=False):
        if self.is_empty_list():
            excess_signals = self.excess_signals()
            self.store_excess_signals(excess_signals + 1)
        else:
            w_process = self.remove_first_link_of_list()
            ProcessWrapper(self.space, w_process).resume(s_current_frame, forced=forced)

    def wait(self, s_current_frame):
        excess = self.excess_signals()
        if excess > 0:
            self.store_excess_signals(excess - 1)
        else:
            new_proc = scheduler(self.space).wake_highest_priority_process()
            self.add_last_link(scheduler(self.space).active_process())
            new_proc.transfer_to_self_from(s_current_frame)


class CriticalSectionWrapper(LinkedListWrapper):

    owner, store_owner = make_getter_setter(2)

    def exit(self, s_current_frame):
        if self.is_empty_list():
            self.store_owner(self.space.w_nil)
        else:
            w_process = self.remove_first_link_of_list()
            self.store_owner(w_process)
            ProcessWrapper(self.space, w_process).resume(s_current_frame)

    def enter(self, s_frame):
        w_active_process = scheduler(self.space).active_process()
        if self.owner().is_nil(self.space):
            self.store_owner(w_active_process)
            s_frame.push(self.space.w_false)
        elif self.owner().is_same_object(w_active_process):
            s_frame.push(self.space.w_true)
        else:
            # arrange to answer false when the process is resumed
            s_frame.push(self.space.w_false)
            self.add_last_link(w_active_process)
            scheduler(self.space).wake_highest_priority_process().transfer_to_self_from(s_frame)

    def test_and_set_owner(self, s_current_frame):
        w_owner = self.owner()
        w_active_process = scheduler(self.space).active_process()
        if w_owner.is_nil(self.space):
            self.store_owner(w_active_process)
            return self.space.w_false
        if w_owner.is_same_object(w_active_process):
            return self.space.w_true
        return self.space.w_nil

class PointWrapper(Wrapper):
    x, store_x = make_int_getter_setter(0)
    y, store_y = make_int_getter_setter(1)

class FormWrapper(Wrapper):
    bits, store_bits = make_getter_setter(constants.FORM_BITS)
    width, store_width = make_int_getter_setter(constants.FORM_WIDTH)
    height, store_height = make_int_getter_setter(constants.FORM_HEIGHT)
    depth, store_depth = make_int_getter_setter(constants.FORM_DEPTH)

    def create_display_bitmap(self):
        w_display_bitmap = from_words_object(self.bits(), self)
        self.store_bits(w_display_bitmap)
        return w_display_bitmap

    def get_display_bitmap(self):
        w_bitmap = self.bits()
        if not isinstance(w_bitmap, W_DisplayBitmap):
            w_display_bitmap = self.create_display_bitmap()
        else:
            w_display_bitmap = w_bitmap
            if w_display_bitmap._depth != self.depth():
                w_display_bitmap = self.create_display_bitmap()
        return w_display_bitmap

    def take_over_display(self):
        self.space.display().set_video_mode(self.width(), self.height(), self.depth())
