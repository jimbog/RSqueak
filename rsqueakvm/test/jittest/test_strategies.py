import py

from .base import BaseJITTest

class TestBasic(BaseJITTest):

     # TODO: there shouldnt be allocations in this
     # The cond_call operations should also not show up...
    @py.test.mark.skipif("'not working'")
    def test_range_asOrderedCollection(self, spy, tmpdir):
        traces = self.run(spy, tmpdir,
        """
        (1 to: 10000) asOrderedCollection.
        """)
        self.assert_matches(traces[0].loop, """
             i197 = getarrayitem_gc(p54, 1, descr=<ArrayS 4>),
             i198 = int_eq(i197, 2147483647),
             guard_false(i198, descr=<Guard0x2eb3450>),
             i199 = int_ge(i197, i190),
             guard_true(i199, descr=<Guard0x2eb33d0>),
             cond_call(i76, 21753520, p68, descr=<Callv 0 r EF=2 OS=121>),
             cond_call(i106, 21753520, p92, descr=<Callv 0 r EF=2 OS=121>),
             cond_call(i106, 21753520, p92, descr=<Callv 0 r EF=2 OS=121>),
             p200 = getarrayitem_gc(p108, 0, descr=<ArrayP 4>),
             cond_call(i106, 21753520, p92, descr=<Callv 0 r EF=2 OS=121>),
             p202 = new_with_vtable(23083336),
             setfield_gc(p202, i190, descr=<FieldS rsqueakvm.model.numeric.W_SmallInteger.inst_value 8>),
             setarrayitem_gc(p108, 1, p202, descr=<ArrayP 4>),
             setarrayitem_gc(p80, 0, p200, descr=<ArrayP 4>),
             setfield_gc(p68, 2, descr=<FieldU rsqueakvm.strategy.ContextPartShadow.inst__stack_ptr 32>),
             setfield_gc(p68, 15, descr=<FieldS rsqueakvm.strategy.ContextPartShadow.inst__pc 24>),
             setfield_gc(p68, p0, descr=<FieldP rsqueakvm.strategy.ContextPartShadow.inst__s_sender 28>),
             setfield_gc(ConstPtr(ptr82), i89, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_remaining_stack_depth 40>),
             setarrayitem_gc(p80, 1, p202, descr=<ArrayP 4>),
             guard_class(p200, 23083152, descr=<Guard0x2eb3350>),
             p203 = getfield_gc(p200, descr=<FieldP rsqueakvm.model.base.W_AbstractObjectWithClassReference.inst_w_class 12>),
             p204 = getfield_gc(p203, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_shadow 16>),
             guard_value(p204, ConstPtr(ptr121), descr=<Guard0x2eb32d0>),
             guard_not_invalidated(descr=<Guard0x2eb3250>),
             p205 = getfield_gc(p200, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_shadow 16>),
             setarrayitem_gc(p80, 0, ConstPtr(null), descr=<ArrayP 4>),
             setfield_gc(p68, 0, descr=<FieldU rsqueakvm.strategy.ContextPartShadow.inst__stack_ptr 32>),
             setfield_gc(ConstPtr(ptr82), i136, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_remaining_stack_depth 40>),
             setarrayitem_gc(p80, 1, ConstPtr(null), descr=<ArrayP 4>),
             guard_class(p205, ConstClass(ListStrategy), descr=<Guard0x2eb31d0>),
             p208 = getfield_gc_pure(p205, descr=<FieldP rsqueakvm.strategy.ListStrategy.inst_storage 16>),
             p209 = getarrayitem_gc(p208, 2, descr=<ArrayP 4>),
             p210 = getarrayitem_gc(p208, 0, descr=<ArrayP 4>),
             guard_class(p210, 23083152, descr=<Guard0x2eb3150>),
             p211 = getfield_gc(p210, descr=<FieldP rsqueakvm.model.base.W_AbstractObjectWithClassReference.inst_w_class 12>),
             p212 = getfield_gc(p211, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_shadow 16>),
             guard_value(p212, ConstPtr(ptr154), descr=<Guard0x2eb30d0>),
             p213 = getfield_gc(p210, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_shadow 16>),
             guard_nonnull_class(p213, 23088412, descr=<Guard0x2eb3050>),
             p214 = getfield_gc_pure(p213, descr=<FieldP rsqueakvm.strategy.SmallIntegerOrNilStrategy.inst_storage 16>),
             i215 = arraylen_gc(p214, descr=<ArrayS 4>),
             i216 = getfield_gc_pure(p213, descr=<FieldU rsqueakvm.strategy.AbstractStrategy.inst_space 12>),
             guard_nonnull_class(p209, 23083336, descr=<Guard0x2ea3f90>),
             i217 = getfield_gc_pure(p209, descr=<FieldS rsqueakvm.model.numeric.W_SmallInteger.inst_value 8>),
             i218 = int_eq(i217, i215),
             guard_false(i218, descr=<Guard0x2ea3f10>),
             i219 = int_add_ovf(i217, 1),
             guard_no_overflow(descr=<Guard0x2ea3e90>),
             i220 = int_ge(i217, 0),
             guard_true(i220, descr=<Guard0x2ea3e10>),
             i221 = int_lt(i217, i215),
             guard_true(i221, descr=<Guard0x2ea3d90>),
             i222 = int_eq(i190, 2147483647),
             guard_false(i222, descr=<Guard0x2ea3d10>),
             setarrayitem_gc(p214, i217, i190, descr=<ArrayS 4>),
             i223 = getarrayitem_gc(p54, 2, descr=<ArrayS 4>),
             setfield_gc(p68, -1, descr=<FieldS rsqueakvm.strategy.ContextPartShadow.inst__pc 24>),
             setfield_gc(p68, ConstPtr(null), descr=<FieldP rsqueakvm.strategy.ContextPartShadow.inst__s_sender 28>),
             setfield_gc(ConstPtr(ptr82), i85, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_remaining_stack_depth 40>),
             i224 = int_eq(i223, 2147483647),
             guard_false(i224, descr=<Guard0x2ea3c90>),
             i225 = int_add_ovf(i190, i223),
             guard_no_overflow(descr=<Guard0x2ea3c10>),
             i226 = int_sub(i193, 5),
             setfield_gc(ConstPtr(ptr82), i226, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>),
             i227 = int_le(i226, 0),
             guard_false(i227, descr=<Guard0x2ea3b90>),
             p228 = new_with_vtable(23083336),
             setfield_gc(p228, i219, descr=<FieldS rsqueakvm.model.numeric.W_SmallInteger.inst_value 8>),
             setarrayitem_gc(p208, 2, p228, descr=<ArrayP 4>),
             i229 = arraylen_gc(p54, descr=<ArrayS 4>),
             i230 = arraylen_gc(p80, descr=<ArrayP 4>),
             i231 = arraylen_gc(p108, descr=<ArrayP 4>),
             jump(p0, p3, p6, i225, p14, p16, p18, p20, p22, p24, p26, p28, p30, p32, p34, p36, p38, p40, p42, p54, i76, p68, i106, p92, p108, p80, i89, i91, i136, i85, i226, descr=TargetToken(48645456))
        """)

    def test_indexOf(self, spy, tmpdir):
        traces = self.run(spy, tmpdir,
        """
        (1 to: 10000000) asOrderedCollection indexOf: 9999999.
        """)
        # First loop: asOrderedCollection, second loop: makeRoomAtLast
        self.assert_matches(traces[2].loop, """
        guard_not_invalidated(descr=<Guard0xf65da5bc>)
        i124 = int_le(i123, i63)
        guard_true(i124, descr=<Guard0x9399668>)
        p98 = force_token()
        enter_portal_frame(0, 0)
        i125 = int_add_ovf(i123, i91)
        guard_no_overflow(descr=<Guard0x939964c>)
        i126 = int_sub(i125, 1)
        i127 = int_gt(i126, i98)
        guard_false(i127, descr=<Guard0x9399614>)
        i128 = int_sub(i126, 1)
        i129 = uint_lt(i128, i111)
        guard_true(i129, descr=<Guard0x93995f8>)
        i130 = int_lt(i128, 0)
        guard_false(i130, descr=<Guard0x93995dc>)
        i131 = getarrayitem_gc_i(p110, i128, descr=<ArrayS 4>)
        i132 = int_eq(i131, 2147483647)
        guard_false(i132, descr=<Guard0x93995a4>)
        leave_portal_frame(0)
        i133 = int_eq(i131, i120)
        guard_false(i133, descr=<Guard0x939956c>)
        i134 = int_add_ovf(i123, 1)
        guard_no_overflow(descr=<Guard0x9399550>)
        i70 = int_sub(i61, 1),
        setfield_gc(ConstPtr(ptr71), i70, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 32>),
        i73 = int_le(i70, 0),
        guard_false(i73, descr=<Guard0x9c13130>),
        i135 = arraylen_gc(p69, descr=<ArrayP 4>)
        jump(p0, p1, i2, p3, p6, p7, i8, i9, p10, p11, i13, p14, p17, p19, p21, i134, p25, p31, p33, p35, p37, p39, p41, p43, p45, p47, p49, p51, p53, i63, p69, p74, p87, i91, i98, p103, p101, i111, p110, i120, descr=TargetToken(154592580))
        """)
