import py

from .base import ModernJITTest

class TestModern(ModernJITTest):
    def test_named_access(self, spy, squeak, tmpdir):
        traces = self.run(spy, squeak, tmpdir, """
        | m |
        m := Morph new.
        1 to: 100000 do: [:i | m bounds ].
        """)
        self.assert_matches(traces[0].loop, """
        guard_not_invalidated(descr=<Guard0xdb8da34>)
        i70 = int_le(i69, 100000)
        guard_true(i70, descr=<Guard0xdc9c7f0>)
        i71 = int_add(i69, 1)
        i72 = arraylen_gc(p65, descr=<ArrayP 4>)
        jump(p0, p1, i2, p3, p6, p7, i8, i9, p10, p11, i13, p14, p17, i71, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, p45, p47, p65, descr=TargetToken(231309508))
        """)

    def test_named_access_in_array(self, spy, squeak, tmpdir):
        traces = self.run(spy, squeak, tmpdir, """
        | o |
        o := Array with: Morph new.
        1 to: 100000 do: [:i | (o at: 1) bounds ].
        """)
        self.assert_matches(traces[0].loop, """
        guard_not_invalidated(descr=<Guard0xdb8da34>)
        i70 = int_le(i69, 100000)
        guard_true(i70, descr=<Guard0xdc9c7f0>)
        i71 = int_add(i69, 1)
        i72 = arraylen_gc(p65, descr=<ArrayP 4>)
        jump(p0, p1, i2, p3, p6, p7, i8, i9, p10, p11, i13, p14, p17, i71, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, p45, p47, p65, descr=TargetToken(231309508))
        """)

    @py.test.mark.skipif("'Not ready'")
    def test_named_access_in_do_block(self, spy, squeak, tmpdir):
        traces = self.run(spy, squeak, tmpdir, """
        | o |
        o := Array with: Morph new.
        1 to: 100000 do: [:i | o do: [:m | m bounds ] ].
        """)
        self.assert_matches(traces[1].loop, """
        guard_not_invalidated(descr=<Guard0xdb8da34>)
        i70 = int_le(i69, 100000)
        guard_true(i70, descr=<Guard0xdc9c7f0>)
        i71 = int_add(i69, 1)
        i72 = arraylen_gc(p65, descr=<ArrayP 4>)
        i73 = arraylen_gc(p67, descr=<ArrayP 4>)
        jump(p0, p1, i2, p3, p6, p7, i8, i9, p10, p11, i13, p14, p17, i71, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, p45, p47, p65, descr=TargetToken(231309508))
        """)

    def test_named_access_fresh(self, spy, squeak, tmpdir):
        traces = self.run(spy, squeak, tmpdir, """
        1 to: 100000 do: [:i | Morph new bounds ].
        """)
        self.assert_matches(traces[0].loop, """
        guard_not_invalidated(descr=<Guard0xe445c70>)
        i169 = int_le(i162, 100000)
        guard_true(i169, descr=<Guard0xe5ec7b8>)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        i170 = int_add(i162, 1)
        i171 = int_sub(i166, 1)
        setfield_gc(ConstPtr(ptr163), i171, descr=<FieldS spyvm.interpreter.Interpreter.inst_interrupt_check_counter 20>)
        i172 = int_le(i171, 0)
        guard_false(i172, descr=<Guard0xe445c9c>)
        i174 = arraylen_gc(p61, descr=<ArrayP 4>)
        i175 = arraylen_gc(p68, descr=<ArrayP 4>)
        i176 = arraylen_gc(p94, descr=<ArrayP 4>)
        i177 = arraylen_gc(p112, descr=<ArrayP 4>)
        i178 = arraylen_gc(p140, descr=<ArrayP 4>)
        jump(p0, p1, i2, p3, p6, p7, i8, i9, p10, p11, i13, p14, i170, p23, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, p45, p47, p61, p68, p63, p94, p112, p114, p140, p142, p154, i171, descr=TargetToken(241143860))
        """)

    def test_named_access_and_send(self, spy, squeak, tmpdir):
        traces = self.run(spy, squeak, tmpdir, """
        | m |
        m := Morph new.
        1 to: 100000 do: [:i | m bounds outsetBy: 10 ].
        """)
        self.assert_matches(traces[3].loop, """
        guard_not_invalidated(descr=<Guard0xdba73ac>),
        i234 = int_le(i227, 100000)
        guard_true(i234, descr=<Guard0xdc6f080>)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        leave_portal_frame(0)
        enter_portal_frame(0, 0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        leave_portal_frame(0)
        enter_portal_frame(0, 0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        i235 = int_add(i227, 1)
        i236 = int_sub(i231, 3)
        setfield_gc(ConstPtr(ptr228), i236, descr=<FieldS spyvm.interpreter.Interpreter.inst_interrupt_check_counter 20>)
        i237 = int_le(i236, 0)
        guard_false(i237, descr=<Guard0xdba7380>)
        i239 = arraylen_gc(p65, descr=<ArrayP 4>)
        i240 = arraylen_gc(p86, descr=<ArrayP 4>)
        i241 = arraylen_gc(p89, descr=<ArrayP 4>)
        i242 = arraylen_gc(p97, descr=<ArrayP 4>)
        i243 = arraylen_gc(p119, descr=<ArrayP 4>)
        i245 = int_sub_ovf(i147, 10)
        guard_no_overflow(descr=<Guard0xdba7354>)
        i246 = int_sub_ovf(i156, 10)
        guard_no_overflow(descr=<Guard0xdba7328>)
        i244 = arraylen_gc(p145, descr=<ArrayS 4>)
        jump(p0, p1, i2, p3, p6, p7, i8, i9, p10, p11, i13, p14, p17, i235, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, p45, p47, p65, p67, p86, p89, p97, p91, p119, p121, p145, p169, p189, p88, i236, i147, i156, descr=TargetToken(231130940))
        """)

    def test_simple_loop_with_closure(self, spy, squeak, tmpdir):
        traces = self.run(spy, squeak, tmpdir, """
        1 to: 100000 do: [:i | [i] value + 100].
        """)
        self.assert_matches(traces[0].loop, """
        guard_not_invalidated(descr=<Guard0x12a02f10>)
        i91 = int_le(i84, 100000)
        guard_true(i91, descr=<Guard0x12a02ee0>)
        enter_portal_frame(0, 0)
        leave_portal_frame(0)
        i92 = int_add(i84, 100)
        i93 = int_add(i84, 1)
        jump(p0, p3, p4, i5, i6, p7, i8, i9, p11, p12, p13, i93, p22, p24, p26, p28, p30, p32, p34, p36, p38, p40, p42, p44, p46, i94, p68, descr=TargetToken(312516328))
        """)
        # self.assert_matches(traces[0].bridges[0], """
        # f26 = call(ConstClass(ll_time.ll_time_time), descr=<Callf 8 EF=4>),
        # setfield_gc(ConstPtr(ptr27), 10000, descr=<FieldS spyvm.interpreter.Interpreter.inst_interrupt_check_counter 20>),
        # guard_no_exception(descr=<Guard0x9161a60>),
        # f30 = float_sub(f26, 1424262084.583439),
        # f32 = float_mul(f30, 1000.000000),
        # i33 = cast_float_to_int(f32),
        # i35 = int_and(i33, 2147483647),
        # i36 = getfield_gc(ConstPtr(ptr27), descr=<FieldS spyvm.interpreter.Interpreter.inst_next_wakeup_tick 28>),
        # i37 = int_is_zero(i36),
        # guard_true(i37, descr=<Guard0x9161bb0>),
        # guard_nonnull(p0, descr=<Guard0x9161b80>),
        # i39 = int_le(i24, 1000000001),
        # guard_true(i39, descr=<Guard0x9161b50>),
        # i40 = getfield_gc_pure(p0, descr=<FieldU spyvm.storage_contexts.ContextPartShadow.inst_is_block_context 69>),
        # guard_value(i40, 0, descr=<Guard0x9161b20>),
        # jump(p0, p1, p2, i3, i4, p5, i6, i7, p8, p9, p10, i24, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, 10000, descr=TargetToken(152597176))
        # """)

    def test_block_passing(self, spy, squeak, tmpdir):
        traces = self.run(spy, squeak, tmpdir, """
        1 to: 100000 do: [:i | [:blk | blk value: i] value: [:x | x + 100]].
        """)
        self.assert_matches(traces[0].loop, """
        guard_not_invalidated(descr=<Guard0x12a02f10>)
        i91 = int_le(i84, 100000)
        guard_true(i91, descr=<Guard0x12a02ee0>)
        enter_portal_frame(0, 0)
        enter_portal_frame(0, 0)
        i92 = int_add(i84, 100)
        leave_portal_frame(0)
        leave_portal_frame(0)
        i93 = int_add(i84, 1)
        jump(p0, p3, p4, i5, i6, p7, i8, i9, p11, p12, p13, i93, p22, p24, p26, p28, p30, p32, p34, p36, p38, p40, p42, p44, p46, i94, p68, descr=TargetToken(312516328))
        """)

    @py.test.mark.skipif("'Not ready'")
    def test_collection_at(self, spy, squeak, tmpdir):
        traces = self.run(spy, squeak, tmpdir, """
        | o |
        o := OrderedCollection newFrom: #(12 13 123 13 1 123 132 132 123 1 213 123 112  2).
        1 to: 100000 do: [:i | o at: 2].
        """)
        self.assert_matches(traces[0].loop, """
        """)

    @py.test.mark.skipif("'Not ready'")
    def test_collect(self, spy, squeak, tmpdir):
        traces = self.run(spy, squeak, tmpdir, """
        | o |
        o := OrderedCollection newFrom: #(12 13 123 13 1 123 132 132 123 1 213 123 112  2).
        1 to: 100000 do: [:i | o collect: [:e | e * 2]].
        """)
        self.assert_matches(traces[0].loop, """
        """)

    @py.test.mark.skipif("'Not ready'")
    def test_inject(self, spy, squeak, tmpdir):
        traces = self.run(spy, squeak, tmpdir, """
        | o |
        o := OrderedCollection newFrom: #(12 13 123 13 1 123 132 132 123 1 213 123 112  2).
        1 to: 100000 do: [:i | o inject: 0 into: [:sum :e | e + sum]].
        """)
        self.assert_matches(traces[0].loop, """
        """)

    def test_mixed_stack(self, spy, squeak, tmpdir):
        traces = self.run(spy, squeak, tmpdir, """
        | a |
        a := 0.
        (1 to: 10000) do: [:i|
          a := ((1 to: 10000) do: [:j| j + i]) last bitOr: a
        ].
        """)
        self.assert_matches(traces[0].loop,
        """
        guard_not_invalidated(descr=<Guard0xd7bd2fc>)
        i133 = int_lt(i76, i58)
        guard_true(i133, descr=<Guard0xd96b630>)
        i134 = int_mul_ovf(i76, i70)
        guard_no_overflow(descr=<Guard0xd96b614>)
        i135 = int_add_ovf(i66, i134)
        guard_no_overflow(descr=<Guard0xd96b5dc>)
        i136 = int_add(i76, 1)
        cond_call(i101, 137066992, p96, descr=<Callv 0 r EF=2 OS=121>)
        enter_portal_frame(0, 0)
        i137 = int_add_ovf(i135, i130)
        guard_no_overflow(descr=<Guard0xd7bd2d0>)
        leave_portal_frame(0)
        i139 = arraylen_gc(p64, descr=<ArrayS 4>)
        jump(p0, p1, i2, p3, p6, p7, i8, i9, p10, p11, i13, p14, p17, i135, i136, p23, i137, p31, p33, p35, p37, p39, p41, p43, p45, p47, p49, i58, p64, i70, i66, p85, p92, p96, i101, p78, i130, p123, p104, descr=TargetToken(227905452))
        """)

    def test_benchFib(self, spy, squeak, tmpdir):
        """Tests how well call_assembler and int-local-return works"""
        traces = self.run(spy, squeak, tmpdir, """
        25 benchFib
        """)
        self.assert_matches(traces[0].bridges[-1], """
        guard_value(i1, 0, descr=<Guard0xd413c70>)
        guard_not_invalidated(descr=<Guard0xd49ecc0>)
        p28 = getfield_gc_r(p9, descr=<FieldP spyvm.model.W_CompiledMethod.inst_version 56 pure>)
        guard_value(p9, ConstPtr(ptr29), descr=<Guard0xd49ec88>)
        guard_value(p28, ConstPtr(ptr30), descr=<Guard0xd49ec50>)
        guard_value(i6, 0, descr=<Guard0xd49ec34>)
        guard_class(p8, ConstClass(W_SmallInteger), descr=<Guard0xd49ec18>)
        i33 = getfield_gc_i(p8, descr=<FieldS spyvm.model.W_SmallInteger.inst_value 8 pure>)
        i35 = int_lt(i33, 2)
        guard_false(i35, descr=<Guard0xd49ebfc>)
        i37 = int_sub(i33, 1)
        i38 = getfield_gc_i(p0, descr=<FieldU spyvm.storage.AbstractStrategy.inst_space 8 pure>)
        p40 = getfield_gc_r(ConstPtr(ptr39), descr=<FieldP spyvm.model.W_PointersObject.inst_strategy 16>)
        guard_value(p40, ConstPtr(ptr41), descr=<Guard0xd413f88>)
        p43 = getfield_gc_r(ConstPtr(ptr42), descr=<FieldP spyvm.model.W_PointersObject.inst_strategy 16>)
        guard_value(p43, ConstPtr(ptr44), descr=<Guard0xd413f5c>)
        p45 = force_token()
        p46 = new_with_vtable(descr=<SizeDescr 64>)
        p48 = new_array_clear(16, descr=<ArrayP 4>)
        setarrayitem_gc(p48, 0, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 1, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 2, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 3, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 4, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 5, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 6, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 7, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 8, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 9, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 10, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 11, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 12, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 13, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 14, ConstPtr(ptr50), descr=<ArrayP 4>)
        setarrayitem_gc(p48, 15, ConstPtr(ptr50), descr=<ArrayP 4>)
        p66 = new_with_vtable(descr=<SizeDescr 12>)
        setfield_gc(p66, i37, descr=<FieldS spyvm.model.W_SmallInteger.inst_value 8 pure>)
        setfield_gc(p46, 142314824, descr=<FieldU spyvm.storage.AbstractStrategy.inst_space 8 pure>)
        setfield_gc(p0, p45, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.vable_token 16>)
        setfield_gc(p46, ConstPtr(ptr68), descr=<FieldP spyvm.storage.AbstractStrategy.inst_w_class 12 pure>)
        setfield_gc(p46, 0, descr=<FieldS spyvm.storage_contexts.ContextPartShadow.inst__pc 20>)
        setfield_gc(p46, p0, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__s_sender 24>)
        setfield_gc(p46, 0, descr=<FieldS spyvm.storage_contexts.ContextPartShadow.inst__stack_ptr 28>)
        setfield_gc(p46, p48, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__temps_and_stack 32>)
        setfield_gc(p46, ConstPtr(ptr71), descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__w_method 36>)
        setfield_gc(p46, p66, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__w_receiver 40>)
        setfield_gc(p46, ConstPtr(null), descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__w_self 44>)
        setfield_gc(p46, 22, descr=<FieldS spyvm.storage_contexts.ContextPartShadow.inst__w_self_size 48>)
        setfield_gc(p46, ConstPtr(null), descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst_closure 52>)
        setfield_gc(p46, ConstPtr(null), descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst_extra_data 56>)
        setfield_gc(p46, ConstPtr(ptr76), descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst_state 60>)
        call_assembler_n(p46, descr=<Loop0>)
        guard_not_forced(descr=<Guard0xd413f30>)
        keepalive(p46)
        p78 = guard_exception(141218848, descr=<Guard0xd413cf4>)
        i79 = ptr_eq(p46, p0)
        guard_false(i79, descr=<Guard0xd413f04>)
        p80 = getfield_gc_r(p46, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.vable_token 16>)
        i82 = ptr_ne(p80, ConstPtr(null))
        cond_call(i82, 137113120, p46, descr=<Callv 0 r EF=2 OS=121>)
        p84 = getfield_gc_r(p46, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst_state 60>)
        i86 = instance_ptr_eq(p84, ConstPtr(ptr85))
        guard_false(i86, descr=<Guard0xd413ed8>)
        guard_not_invalidated(descr=<Guard0xd49eb00>)
        p87 = getfield_gc_r(p46, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst_closure 52>)
        guard_isnull(p87, descr=<Guard0xd49ea90>)
        p88 = getfield_gc_r(p46, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__w_method 36>)
        p89 = getfield_gc_r(p88, descr=<FieldP spyvm.model.W_CompiledMethod.inst_version 56 pure>)
        guard_value(p88, ConstPtr(ptr90), descr=<Guard0xd49ea3c>)
        guard_value(p89, ConstPtr(ptr91), descr=<Guard0xd49e9cc>)
        p92 = getfield_gc_r(p46, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__s_sender 24>)
        setfield_gc(p46, -1, descr=<FieldS spyvm.storage_contexts.ContextPartShadow.inst__pc 20>)
        guard_nonnull(p92, descr=<Guard0xd413eac>)
        setfield_gc(p46, ConstPtr(null), descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__s_sender 24>)
        guard_class(p78, 141218848, descr=<Guard0xd413e80>)
        i96 = getfield_gc_i(p78, descr=<FieldS spyvm.interpreter.IntLocalReturn.inst__value 8 pure>)
        i98 = int_sub(i33, 2)
        p100 = getfield_gc_r(ConstPtr(ptr99), descr=<FieldP spyvm.model.W_PointersObject.inst_strategy 16>)
        setfield_gc(p46, ConstPtr(ptr101), descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst_state 60>)
        guard_value(p100, ConstPtr(ptr102), descr=<Guard0xd413e54>)
        p104 = getfield_gc_r(ConstPtr(ptr103), descr=<FieldP spyvm.model.W_PointersObject.inst_strategy 16>)
        guard_value(p104, ConstPtr(ptr105), descr=<Guard0xd413e28>)
        p106 = force_token()
        p107 = new_with_vtable(descr=<SizeDescr 64>)
        p109 = new_array_clear(16, descr=<ArrayP 4>)
        setarrayitem_gc(p109, 0, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 1, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 2, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 3, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 4, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 5, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 6, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 7, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 8, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 9, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 10, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 11, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 12, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 13, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 14, ConstPtr(ptr111), descr=<ArrayP 4>)
        setarrayitem_gc(p109, 15, ConstPtr(ptr111), descr=<ArrayP 4>)
        p127 = new_with_vtable(descr=<SizeDescr 12>)
        setfield_gc(p127, i98, descr=<FieldS spyvm.model.W_SmallInteger.inst_value 8 pure>)
        setfield_gc(p107, 142314824, descr=<FieldU spyvm.storage.AbstractStrategy.inst_space 8 pure>)
        setfield_gc(p0, p106, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.vable_token 16>)
        setfield_gc(p107, ConstPtr(ptr129), descr=<FieldP spyvm.storage.AbstractStrategy.inst_w_class 12 pure>)
        setfield_gc(p107, 0, descr=<FieldS spyvm.storage_contexts.ContextPartShadow.inst__pc 20>)
        setfield_gc(p107, p0, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__s_sender 24>)
        setfield_gc(p107, 0, descr=<FieldS spyvm.storage_contexts.ContextPartShadow.inst__stack_ptr 28>)
        setfield_gc(p107, p109, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__temps_and_stack 32>)
        setfield_gc(p107, ConstPtr(ptr132), descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__w_method 36>)
        setfield_gc(p107, p127, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__w_receiver 40>)
        setfield_gc(p107, ConstPtr(null), descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__w_self 44>)
        setfield_gc(p107, 22, descr=<FieldS spyvm.storage_contexts.ContextPartShadow.inst__w_self_size 48>)
        setfield_gc(p107, ConstPtr(null), descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst_closure 52>)
        setfield_gc(p107, ConstPtr(null), descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst_extra_data 56>)
        setfield_gc(p107, ConstPtr(ptr137), descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst_state 60>)
        call_assembler_n(p107, descr=<Loop0>)
        guard_not_forced(descr=<Guard0xd413dfc>)
        keepalive(p107)
        p139 = guard_exception(141218848, descr=<Guard0xd413cc8>)
        i140 = ptr_eq(p107, p0)
        guard_false(i140, descr=<Guard0xd413dd0>)
        p141 = getfield_gc_r(p107, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.vable_token 16>)
        i142 = ptr_ne(p141, ConstPtr(null))
        cond_call(i142, 137113120, p107, descr=<Callv 0 r EF=2 OS=121>)
        p144 = getfield_gc_r(p107, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst_state 60>)
        i146 = instance_ptr_eq(p144, ConstPtr(ptr145))
        guard_false(i146, descr=<Guard0xd413da4>)
        guard_not_invalidated(descr=<Guard0xd49e87c>)
        p147 = getfield_gc_r(p107, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst_closure 52>)
        guard_isnull(p147, descr=<Guard0xd49e80c>)
        p148 = getfield_gc_r(p107, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__w_method 36>)
        p149 = getfield_gc_r(p148, descr=<FieldP spyvm.model.W_CompiledMethod.inst_version 56 pure>)
        guard_value(p148, ConstPtr(ptr150), descr=<Guard0xd49e7b8>)
        guard_value(p149, ConstPtr(ptr151), descr=<Guard0xd49e748>)
        p152 = getfield_gc_r(p107, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__s_sender 24>)
        setfield_gc(p107, -1, descr=<FieldS spyvm.storage_contexts.ContextPartShadow.inst__pc 20>)
        guard_nonnull(p152, descr=<Guard0xd413d78>)
        setfield_gc(p107, ConstPtr(null), descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst__s_sender 24>)
        guard_class(p139, 141218848, descr=<Guard0xd413d4c>)
        i156 = getfield_gc_i(p139, descr=<FieldS spyvm.interpreter.IntLocalReturn.inst__value 8 pure>)
        setfield_gc(p107, ConstPtr(ptr157), descr=<FieldP spyvm.storage_contexts.ContextPartShadow.inst_state 60>)
        i158 = int_add_ovf(i96, i156)
        guard_no_overflow(descr=<Guard0xd413d20>)
        i161 = int_add_ovf(i158, 1)
        guard_no_overflow(descr=<Guard0xd49e6bc>)
        guard_isnull(p7, descr=<Guard0xd49e684>)
        i163 = instance_ptr_eq(p4, ConstPtr(ptr162))
        guard_false(i163, descr=<Guard0xd49e668>)
        leave_portal_frame(0)
        p165 = force_token()
        setfield_gc(p0, p165, descr=<FieldP spyvm.storage_contexts.ContextPartShadow.vable_token 16>)
        p166 = new_with_vtable(descr=<SizeDescr 12>)
        setfield_gc(p166, i161, descr=<FieldS spyvm.interpreter.IntLocalReturn.inst__value 8 pure>)
        guard_not_forced_2(descr=<Guard0xd413c9c>)
        finish(p166, descr=<ExitFrameWithExceptionDescrRef object at 0x87147b0>)
        """)
