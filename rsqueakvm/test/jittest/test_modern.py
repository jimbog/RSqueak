import py

from .base import ModernJITTest

from rsqueakvm.util.system import IS_64BIT

class TestModern(ModernJITTest):
    def test_init(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | c |
        Object
            subclass: #MyA
            instanceVariableNames: 'i'
            classVariableNames: ''
            poolDictionaries: ''
            category: 'Test'.
        c := Smalltalk at: #MyA.
        c compile: 'initialize
i := 1.' classified: 'none' withStamp: nil notifying: nil logSource: false.
        1 to: 100000 do: [:i | c new ].
        """)
        self.assert_matches(traces[-1].loop, """
        guard_not_invalidated(descr=<Guard0xb06c3c8>)
        i88 = int_le(i79, 100000)
        guard_true(i88, descr=<Guard0xb051148>)
        p89 = force_token()
        enter_portal_frame(4, 0)
        p92 = force_token()
        enter_portal_frame(4, 0)
        leave_portal_frame(4)
        leave_portal_frame(4)
        i98 = int_add(i79, 1)
        i100 = int_sub(i83, 1)
        setfield_gc(ConstPtr(ptr101), i100, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        i103 = int_le(i100, 0)
        guard_false(i103, descr=<Guard0xb06c498>)
        jump(p0, p1, i2, p3, p4, p7, p8, p10, p13, i98, p21, p23, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, i100, descr=TargetToken(183580560))
        """)

    def test_ivar_access(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | c o |
        Object
            subclass: #MyA
            instanceVariableNames: 'i'
            classVariableNames: ''
            poolDictionaries: ''
            category: 'Test'.
        c := Smalltalk at: #MyA.
        c compile: 'initialize
i := 1.' classified: 'none' withStamp: nil notifying: nil logSource: false.
        c compile: 'i
^ i' classified: 'none' withStamp: nil notifying: nil logSource: false.
        c compile: 'i: n
i := n' classified: 'none' withStamp: nil notifying: nil logSource: false.
        o := c new.
        [ o i < 10000 ] whileTrue: [ o i: o i + 1 ].
        """)
        self.assert_matches(traces[-1].loop, """
        guard_not_invalidated(descr=<Guard0xa4a48a8>)
        i78 = int_lt(i61, 10000)
        guard_true(i78, descr=<Guard0xa485c40>)
        i80 = int_add(i61, 1)
        p81 = force_token()
        enter_portal_frame(4, 0)
        leave_portal_frame(4)
        i86 = int_sub(i72, 1)
        setfield_gc(ConstPtr(ptr87), i86, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        setarrayitem_gc(p53, 0, i80, descr=<ArrayS 8>)
        i90 = int_le(i86, 0)
        guard_false(i90, descr=<Guard0xa4a4f90>)
        i91 = arraylen_gc(p53, descr=<ArrayS 8>)
        jump(p0, p1, i2, p3, p4, p7, p8, p10, p13, p15, p23, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, p53, i80, i86, descr=TargetToken(170868656))
        """)

    def test_named_access(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | m |
        m := Morph new.
        1 to: 100000 do: [:i | m bounds ].
        """)
        self.assert_matches(traces[0].loop, """
        guard_not_invalidated(descr=<Guard0xdb8da34>)
        i69 = int_le(i69, 100000)
        guard_true(i69, descr=<Guard0xdc9c7f0>)
        i71 = int_add(i69, 1)
        i70 = int_sub(i61, 1),
        setfield_gc(ConstPtr(ptr71), i70, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 32>),
        i73 = int_le(i70, 0),
        guard_false(i73, descr=<Guard0x9c13130>),
        i72 = arraylen_gc(p65, descr=<ArrayP 4>)
        jump(p0, p1, i2, p3, p6, p7, i8, i9, p10, p11, i13, p14, p17, i71, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, p45, p47, p65, descr=TargetToken(231309508))
        """)

    def test_named_access_in_array(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | o |
        o := Array with: Morph new.
        1 to: 100000 do: [:i | (o at: 1) bounds ].
        """)
        self.assert_matches(traces[0].loop, """
        guard_not_invalidated(descr=<Guard0xdb8da34>)
        i70 = int_le(i69, 100000)
        guard_true(i70, descr=<Guard0xdc9c7f0>)
        i71 = int_add(i69, 1)
        i73 = int_sub(i61, 1),
        setfield_gc(ConstPtr(ptr71), i70, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 32>),
        i74 = int_le(i73, 0),
        guard_false(i74, descr=<Guard0x9c13130>),
        i72 = arraylen_gc(p65, descr=<ArrayP 4>)
        jump(p0, p1, i2, p3, p6, p7, i8, i9, p10, p11, i13, p14, p17, i71, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, p45, p47, p65, descr=TargetToken(231309508))
        """)

    @py.test.mark.skipif("'Not ready'")
    def test_named_access_in_do_block(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
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

    def test_named_access_fresh(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        1 to: 100000 do: [:i | Morph new bounds ].
        """)
        self.assert_matches(traces[0].loop, """
        guard_not_invalidated(descr=<Guard0xe445c70>)
        i169 = int_le(i162, 100000)
        guard_true(i169, descr=<Guard0xe5ec7b8>)
        p98 = force_token()
        enter_portal_frame(0, 0)
        p99 = force_token()
        enter_portal_frame(0, 0)
        p100 = force_token()
        enter_portal_frame(0, 0)
        p101 = force_token()
        enter_portal_frame(0, 0)
        p102 = force_token()
        enter_portal_frame(0, 0)
        p103 = force_token()
        enter_portal_frame(0, 0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        p104 = force_token()
        enter_portal_frame(0, 0)
        p105 = force_token()
        enter_portal_frame(0, 0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        leave_portal_frame(0)
        i170 = int_add(i162, 1)
        i171 = int_sub(i166, 1)
        setfield_gc(ConstPtr(ptr163), i171, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 20>)
        i172 = int_le(i171, 0)
        guard_false(i172, descr=<Guard0xe445c9c>)
        i174 = arraylen_gc(p61, descr=<ArrayP 4>)
        i175 = arraylen_gc(p68, descr=<ArrayP 4>)
        i176 = arraylen_gc(p94, descr=<ArrayP 4>)
        i177 = arraylen_gc(p112, descr=<ArrayP 4>)
        i178 = arraylen_gc(p140, descr=<ArrayP 4>)
        jump(p0, p1, i2, p3, p6, p7, i8, i9, p10, p11, i13, p14, i170, p23, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, p45, p47, p61, p68, p63, p94, p112, p114, p140, p142, p154, i171, descr=TargetToken(241143860))
        """)

    def test_named_access_and_send(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | m |
        m := Morph new.
        1 to: 100000 do: [:i | m bounds outsetBy: 10 ].
        """)
        self.assert_matches(traces[3].loop, """
        guard_not_invalidated(descr=<Guard0xdba73ac>),
        i234 = int_le(i227, 100000)
        guard_true(i234, descr=<Guard0xdc6f080>)
        p98 = force_token()
        enter_portal_frame(4, 0)
        p99 = force_token()
        enter_portal_frame(4, 0)
        p100 = force_token()
        enter_portal_frame(4, 0)
        p101 = force_token()
        enter_portal_frame(4, 0)
        leave_portal_frame(4)
        leave_portal_frame(4)
        leave_portal_frame(4)
        p102 = force_token()
        enter_portal_frame(4, 0)
        p103 = force_token()
        enter_portal_frame(4, 0)
        p104 = force_token()
        enter_portal_frame(4, 0)
        leave_portal_frame(4)
        leave_portal_frame(4)
        leave_portal_frame(4)
        p105 = force_token()
        enter_portal_frame(4, 0)
        p106 = force_token()
        enter_portal_frame(4, 0)
        leave_portal_frame(4)
        leave_portal_frame(4)
        leave_portal_frame(4)
        i235 = int_add(i227, 1)
        i236 = int_sub(i231, 3)
        setfield_gc(ConstPtr(ptr228), i236, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 20>)
        i237 = int_le(i236, 0)
        guard_false(i237, descr=<Guard0xdba7380>)
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

    def test_simple_loop_with_closure(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        1 to: 100000 do: [:i | [i] value + 100].
        """)
        self.assert_matches(traces[0].loop, """
        guard_not_invalidated(descr=<Guard0x12a02f10>)
        i91 = int_le(i84, 100000)
        guard_true(i91, descr=<Guard0x12a02ee0>)
        p98 = force_token()
        enter_portal_frame(0, 0)
        leave_portal_frame(0)
        i92 = int_add(i84, 100)
        i93 = int_add(i84, 1)
        i70 = int_sub(i61, 1),
        setfield_gc(ConstPtr(ptr71), i70, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 32>),
        i73 = int_le(i70, 0),
        guard_false(i73, descr=<Guard0x9c13130>),
        jump(p0, p3, p4, i5, i6, p7, i8, i9, p11, p12, p13, i93, p22, p24, p26, p28, p30, p32, p34, p36, p38, p40, p42, p44, p46, i94, p68, descr=TargetToken(312516328))
        """)
        # self.assert_matches(traces[0].bridges[0], """
        # f26 = call(ConstClass(ll_time.ll_time_time), descr=<Callf 8 EF=4>),
        # setfield_gc(ConstPtr(ptr27), 10000, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 20>),
        # guard_no_exception(descr=<Guard0x9161a60>),
        # f30 = float_sub(f26, 1424262084.583439),
        # f32 = float_mul(f30, 1000.000000),
        # i33 = cast_float_to_int(f32),
        # i35 = int_and(i33, 2147483647),
        # i36 = getfield_gc(ConstPtr(ptr27), descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_next_wakeup_tick 28>),
        # i37 = int_is_zero(i36),
        # guard_true(i37, descr=<Guard0x9161bb0>),
        # guard_nonnull(p0, descr=<Guard0x9161b80>),
        # i39 = int_le(i24, 1000000001),
        # guard_true(i39, descr=<Guard0x9161b50>),
        # i40 = getfield_gc_pure(p0, descr=<FieldU rsqueakvm.storage_contexts.ContextPartShadow.inst_is_block_context 69>),
        # guard_value(i40, 0, descr=<Guard0x9161b20>),
        # jump(p0, p1, p2, i3, i4, p5, i6, i7, p8, p9, p10, i24, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, 10000, descr=TargetToken(152597176))
        # """)

    def test_block_passing(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        1 to: 100000 do: [:i | [:blk | blk value: i] value: [:x | x + 100]].
        """)
        self.assert_matches(traces[0].loop, """
        guard_not_invalidated(descr=<Guard0x12a02f10>)
        i91 = int_le(i84, 100000)
        guard_true(i91, descr=<Guard0x12a02ee0>)
        p98 = force_token()
        enter_portal_frame(0, 0)
        p99 = force_token()
        enter_portal_frame(0, 0)
        i92 = int_add(i84, 100)
        leave_portal_frame(0)
        leave_portal_frame(0)
        i93 = int_add(i84, 1)
        i70 = int_sub(i61, 1),
        setfield_gc(ConstPtr(ptr71), i70, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 32>),
        i73 = int_le(i70, 0),
        guard_false(i73, descr=<Guard0x9c13130>),
        jump(p0, p3, p4, i5, i6, p7, i8, i9, p11, p12, p13, i93, p22, p24, p26, p28, p30, p32, p34, p36, p38, p40, p42, p44, p46, i94, p68, descr=TargetToken(312516328))
        """)

    @py.test.mark.skipif("'Not ready'")
    def test_collection_at(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | o |
        o := OrderedCollection newFrom: #(12 13 123 13 1 123 132 132 123 1 213 123 112  2).
        1 to: 100000 do: [:i | o at: 2].
        """)
        self.assert_matches(traces[0].loop, """
        """)

    @py.test.mark.skipif("'Not ready'")
    def test_collect(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | o |
        o := OrderedCollection newFrom: #(12 13 123 13 1 123 132 132 123 1 213 123 112  2).
        1 to: 100000 do: [:i | o collect: [:e | e * 2]].
        """)
        self.assert_matches(traces[0].loop, """
        """)

    @py.test.mark.skipif("'Not ready'")
    def test_inject(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | o |
        o := OrderedCollection newFrom: #(12 13 123 13 1 123 132 132 123 1 213 123 112  2).
        1 to: 100000 do: [:i | o inject: 0 into: [:sum :e | e + sum]].
        """)
        self.assert_matches(traces[0].loop, """
        """)

    def test_mixed_stack(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | a |
        a := 0.
        (1 to: 10000) do: [:i|
          a := ((1 to: 10000) do: [:j| j + i]) last bitOr: a
        ].
        """)
        self.assert_matches(traces[0].loop,
        """
        guard_not_invalidated(descr=<Guard0x4ab0498>)
        i102 = int_lt(i66, i49)
        guard_true(i102, descr=<Guard0x65a22a8>)
        i103 = int_mul_ovf(i66, i60)
        guard_no_overflow(descr=<Guard0x65a2260>)
        i104 = int_add_ovf(i56, i103)
        guard_no_overflow(descr=<Guard0x65a2218>)
        i106 = int_add(i66, 1)
        p107 = force_token()
        enter_portal_frame(1, 0)
        i110 = int_add_ovf(i104, i92)
        guard_no_overflow(descr=<Guard0x65a2188>)
        leave_portal_frame(1)
        i113 = int_sub(i98, 1)
        setfield_gc(ConstPtr(ptr114), i113, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        i116 = int_le(i113, 0)
        guard_false(i116, descr=<Guard0x4ab0430>)
        i118 = arraylen_gc(p54, descr=<ArrayS 8>)
        jump(p0, p1, i2, p4, p5, p6, p8, p11, i104, i106, p17, i110, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, i49, p54, i60, i56, p77, p87, i92, i113, descr=TargetToken(106653920))
        """)

    def test_global_class_access(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | a |
        a := nil.
        (1 to: 1000000) do: [:i|
           a := OrderedCollection compilerClass.
        ].
        """)
        self.assert_matches(traces[0].loop,
        """
        guard_not_invalidated(descr=<Guard0x9ee1c90>),
        i146 = int_lt(i69, i52),
        guard_true(i146, descr=<Guard0x9fda218>),
        i147 = int_mul_ovf(i69, i63),
        guard_no_overflow(descr=<Guard0x9fda1d0>),
        i148 = int_add_ovf(i59, i147),
        guard_no_overflow(descr=<Guard0x9fda140>),
        i150 = int_add(i69, 1),
        p153 = getarrayitem_gc_r(p88, 0, descr=<ArrayP 8>),
        guard_nonnull_class(p153, ConstClass(W_PointersObject), descr=<Guard0xaf52454>)
        p98 = force_token()
        enter_portal_frame(4, 0),
        p99 = force_token()
        enter_portal_frame(4, 0),
        leave_portal_frame(4),
        p161 = getfield_gc_r(p153, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>),
        guard_value(p161, ConstPtr(ptr162), descr=<Guard0x9ee1bc0>),
        p163 = getfield_gc_r(p153, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst__storage 24>),
        leave_portal_frame(4),
        i166 = int_sub(i140, 1),
        setfield_gc(ConstPtr(ptr167), i166, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>),
        setarrayitem_gc(p163, 0, p145, descr=<ArrayP 8>),
        i170 = int_le(i166, 0),
        guard_false(i170, descr=<Guard0x9ee1b58>),
        i171 = arraylen_gc(p57, descr=<ArrayS 8>),
        i172 = arraylen_gc(p106, descr=<ArrayP 8>),
        i173 = arraylen_gc(p124, descr=<ArrayP 8>),
        jump(p0, p1, i2, p3, p4, p7, p8, p10, p13, i148, i150, p19, p145, p27, p29, p31, p33, p35, p37, p39, p41, p43, p45, i52, p57, i63, i59, p74, p75, i80, p88, p106, p108, p111, p124, p145, p83, i166, descr=TargetToken(166580560))
        """)

    @py.test.mark.skipif("'Flaky, check with pypy devs'")
    def test_benchFib(self, spy, tmpdir):
        """Tests how well call_assembler and int-local-return works"""
        traces = self.run(spy, tmpdir, """
        25 benchFib
        """)
        self.assert_matches(traces[0].bridges[-1], """
        guard_value(i7, 0, descr=<Guard0xa655430>),
        guard_not_invalidated(descr=<Guard0xa67d4d0>),
        guard_value(p1, ConstPtr(ptr28), descr=<Guard0xa67d4b0>),
        guard_value(i2, 0, descr=<Guard0xa67d470>),
        guard_class(p8, ConstClass(W_SmallInteger), descr=<Guard0xa67d3f0>),
        i31 = getfield_gc_i(p8, descr=<FieldS rsqueakvm.model.numeric.W_SmallInteger.inst_value 8 pure>),
        i33 = int_lt(i31, 2),
        guard_false(i33, descr=<Guard0xa67d3b0>),
        i35 = int_sub(i31, 1),
        i36 = getfield_gc_i(p0, descr=<FieldU rsqueakvm.storage.AbstractStrategy.inst_space 8 pure>),
        p38 = getfield_gc_r(ConstPtr(ptr37), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 20>),
        guard_value(p38, ConstPtr(ptr39), descr=<Guard0xa655730>),
        p41 = getfield_gc_r(ConstPtr(ptr40), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 20>),
        guard_value(p41, ConstPtr(ptr42), descr=<Guard0xa655700>),
        p43 = new_with_vtable(descr=<SizeDescr 64>),
        p45 = new_array_clear(16, descr=<ArrayP 4>),
        setarrayitem_gc(p45, 0, ConstPtr(ptr47), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 1, ConstPtr(ptr49), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 2, ConstPtr(ptr51), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 3, ConstPtr(ptr53), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 4, ConstPtr(ptr55), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 5, ConstPtr(ptr57), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 6, ConstPtr(ptr59), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 7, ConstPtr(ptr61), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 8, ConstPtr(ptr63), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 9, ConstPtr(ptr65), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 10, ConstPtr(ptr67), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 11, ConstPtr(ptr69), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 12, ConstPtr(ptr71), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 13, ConstPtr(ptr73), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 14, ConstPtr(ptr75), descr=<ArrayP 4>),
        setarrayitem_gc(p45, 15, ConstPtr(ptr77), descr=<ArrayP 4>),
        p78 = new_with_vtable(descr=<SizeDescr 12>),
        setfield_gc(p78, i35, descr=<FieldS rsqueakvm.model.numeric.W_SmallInteger.inst_value 8 pure>),
        setfield_gc(p43, 6371376, descr=<FieldU rsqueakvm.storage.AbstractStrategy.inst_space 8 pure>),
        setfield_gc(p43, ConstPtr(ptr80), descr=<FieldP rsqueakvm.storage.AbstractStrategy.inst_w_class 12 pure>),
        setfield_gc(p43, 0, descr=<FieldS rsqueakvm.storage_contexts.ContextPartShadow.inst__pc 20>),
        setfield_gc(p43, p0, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__s_sender 24>),
        setfield_gc(p43, 0, descr=<FieldS rsqueakvm.storage_contexts.ContextPartShadow.inst__stack_ptr 28>),
        setfield_gc(p43, p45, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__temps_and_stack 32>),
        setfield_gc(p43, ConstPtr(ptr83), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__w_method 36>),
        setfield_gc(p43, p78, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__w_receiver 40>),
        setfield_gc(p43, ConstPtr(null), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__w_self 44>),
        setfield_gc(p43, 22, descr=<FieldS rsqueakvm.storage_contexts.ContextPartShadow.inst__w_self_size 48>),
        setfield_gc(p43, ConstPtr(null), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_closure 52>),
        setfield_gc(p43, ConstPtr(null), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_extra_data 56>),
        setfield_gc(p43, ConstPtr(ptr88), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_state 60>),
        call_assembler_n(p43, descr=<Loop0>),
        guard_not_forced(descr=<Guard0xa4bfcdc>),
        keepalive(p43),
        p90 = guard_exception(4706660, descr=<Guard0xa6554c0>),
        i91 = ptr_eq(p43, p0),
        guard_false(i91, descr=<Guard0xa6556d0>),
        p92 = getfield_gc_r(p43, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.vable_token 16>),
        i94 = ptr_ne(p92, ConstPtr(null)),
        cond_call(i94, 1442416, p43, descr=<Callv 0 r EF=2 OS=121>),
        p96 = getfield_gc_r(p43, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_state 60>),
        i98 = instance_ptr_eq(p96, ConstPtr(ptr97)),
        guard_false(i98, descr=<Guard0xa6556a0>),
        guard_not_invalidated(descr=<Guard0xa67d2b0>),
        p99 = getfield_gc_r(p43, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_closure 52>),
        guard_isnull(p99, descr=<Guard0xa67d290>),
        p100 = getfield_gc_r(p43, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__w_method 36>),
        guard_value(p100, ConstPtr(ptr101), descr=<Guard0xa67d270>),
        p102 = getfield_gc_r(p43, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__s_sender 24>),
        setfield_gc(p43, -1, descr=<FieldS rsqueakvm.storage_contexts.ContextPartShadow.inst__pc 20>),
        guard_nonnull(p102, descr=<Guard0xa655670>),
        setfield_gc(p43, ConstPtr(null), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__s_sender 24>),
        guard_class(p90, 4706660, descr=<Guard0xa655640>),
        i106 = getfield_gc_i(p90, descr=<FieldS rsqueakvm.interpreter.IntLocalReturn.inst__value 8 pure>),
        i108 = int_sub(i31, 2),
        p110 = getfield_gc_r(ConstPtr(ptr109), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 20>),
        setfield_gc(p43, ConstPtr(ptr111), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_state 60>),
        guard_value(p110, ConstPtr(ptr112), descr=<Guard0xa655610>),
        p114 = getfield_gc_r(ConstPtr(ptr113), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 20>),
        guard_value(p114, ConstPtr(ptr115), descr=<Guard0xa6555e0>),
        p116 = new_with_vtable(descr=<SizeDescr 64>),
        p118 = new_array_clear(16, descr=<ArrayP 4>),
        setarrayitem_gc(p118, 0, ConstPtr(ptr120), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 1, ConstPtr(ptr122), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 2, ConstPtr(ptr124), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 3, ConstPtr(ptr126), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 4, ConstPtr(ptr128), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 5, ConstPtr(ptr130), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 6, ConstPtr(ptr132), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 7, ConstPtr(ptr134), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 8, ConstPtr(ptr136), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 9, ConstPtr(ptr138), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 10, ConstPtr(ptr140), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 11, ConstPtr(ptr142), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 12, ConstPtr(ptr144), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 13, ConstPtr(ptr146), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 14, ConstPtr(ptr148), descr=<ArrayP 4>),
        setarrayitem_gc(p118, 15, ConstPtr(ptr150), descr=<ArrayP 4>),
        p151 = new_with_vtable(descr=<SizeDescr 12>),
        setfield_gc(p151, i108, descr=<FieldS rsqueakvm.model.numeric.W_SmallInteger.inst_value 8 pure>),
        setfield_gc(p116, 6371376, descr=<FieldU rsqueakvm.storage.AbstractStrategy.inst_space 8 pure>),
        setfield_gc(p116, ConstPtr(ptr153), descr=<FieldP rsqueakvm.storage.AbstractStrategy.inst_w_class 12 pure>),
        setfield_gc(p116, 0, descr=<FieldS rsqueakvm.storage_contexts.ContextPartShadow.inst__pc 20>),
        setfield_gc(p116, p0, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__s_sender 24>),
        setfield_gc(p116, 0, descr=<FieldS rsqueakvm.storage_contexts.ContextPartShadow.inst__stack_ptr 28>),
        setfield_gc(p116, p118, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__temps_and_stack 32>),
        setfield_gc(p116, ConstPtr(ptr156), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__w_method 36>),
        setfield_gc(p116, p151, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__w_receiver 40>),
        setfield_gc(p116, ConstPtr(null), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__w_self 44>),
        setfield_gc(p116, 22, descr=<FieldS rsqueakvm.storage_contexts.ContextPartShadow.inst__w_self_size 48>),
        setfield_gc(p116, ConstPtr(null), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_closure 52>),
        setfield_gc(p116, ConstPtr(null), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_extra_data 56>),
        setfield_gc(p116, ConstPtr(ptr161), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_state 60>),
        call_assembler_n(p116, descr=<Loop0>),
        guard_not_forced(descr=<Guard0xa4bfca8>),
        keepalive(p116),
        p163 = guard_exception(4706660, descr=<Guard0xa655490>),
        i164 = ptr_eq(p116, p0),
        guard_false(i164, descr=<Guard0xa6555b0>),
        p165 = getfield_gc_r(p116, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.vable_token 16>),
        i167 = ptr_ne(p165, ConstPtr(null)),
        cond_call(i167, 1442416, p116, descr=<Callv 0 r EF=2 OS=121>),
        p169 = getfield_gc_r(p116, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_state 60>),
        i171 = instance_ptr_eq(p169, ConstPtr(ptr170)),
        guard_false(i171, descr=<Guard0xa655580>),
        guard_not_invalidated(descr=<Guard0xa67d150>),
        p172 = getfield_gc_r(p116, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_closure 52>),
        guard_isnull(p172, descr=<Guard0xa67d130>),
        p173 = getfield_gc_r(p116, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__w_method 36>),
        guard_value(p173, ConstPtr(ptr174), descr=<Guard0xa67d110>),
        p175 = getfield_gc_r(p116, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__s_sender 24>),
        setfield_gc(p116, -1, descr=<FieldS rsqueakvm.storage_contexts.ContextPartShadow.inst__pc 20>),
        guard_nonnull(p175, descr=<Guard0xa655550>),
        setfield_gc(p116, ConstPtr(null), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__s_sender 24>),
        guard_class(p163, 4706660, descr=<Guard0xa655520>),
        i179 = getfield_gc_i(p163, descr=<FieldS rsqueakvm.interpreter.IntLocalReturn.inst__value 8 pure>),
        setfield_gc(p116, ConstPtr(ptr180), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_state 60>),
        i181 = int_add_ovf(i106, i179),
        guard_no_overflow(descr=<Guard0xa6554f0>),
        i184 = int_add_ovf(i181, 1),
        guard_no_overflow(descr=<Guard0xa67d050>),
        guard_isnull(p4, descr=<Guard0xa67d010>),
        i186 = instance_ptr_eq(p6, ConstPtr(ptr185)),
        guard_false(i186, descr=<Guard0xa665fd0>),
        leave_portal_frame(4),
        p188 = force_token(),
        setfield_gc(p0, p188, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.vable_token 16>),
        p189 = new_with_vtable(descr=<SizeDescr 12>),
        setfield_gc(p189, i184, descr=<FieldS rsqueakvm.interpreter.IntLocalReturn.inst__value 8 pure>),
        guard_not_forced_2(descr=<Guard0xa4bfc74>),
        finish(p189, descr=<ExitFrameWithExceptionDescrRef object at 0x5835f8>)
        """)

    def test_make_float(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | a |
        1 to: 1000000 do: [:i|
           a := (Float basicNew: 2).
           a basicAt: 1 put: i.
           a basicAt: 2 put: i.
           a + 2.
        ].
        """)
        if IS_64BIT:
            self.assert_matches(traces[1].loop,
            """
            guard_not_invalidated(descr=<Guard0xa745f00>)
            i124 = int_le(i115, 1000000)
            guard_true(i124, descr=<Guard0xa75d148>)
            p125 = force_token()
            enter_portal_frame(4, 0)
            i129 = int_and(i115, 4294967295)
            leave_portal_frame(4)
            p131 = force_token()
            enter_portal_frame(4, 0)
            leave_portal_frame(4)
            i136 = int_lshift(i129, 32)
            i137 = int_or(i136, i129)
            i139 = uint_rshift(i137, 63)
            i141 = int_and(i137, 9218868437227405312)
            i143 = uint_rshift(i141, 52)
            i145 = int_and(i137, 4503599627370495)
            guard_value(i143, 0, descr=<Guard0xa75d190>)
            f148 = call_f(ConstClass(_ll_1_cast_uint_to_float__Unsigned), i145, descr=<Callf 8 i EF=2>)
            i150 = float_eq(f148, 0.000000)
            guard_false(i150, descr=<Guard0xa745f68>)
            f152 = float_sub(f148, f148)
            i154 = float_eq(f152, 0.000000)
            guard_true(i154, descr=<Guard0xa75d1d8>)
            f157 = call_f(ConstClass(ccall_ldexp), f148, -1074, descr=<Callf 8 fi EF=2>)
            i160 = call_i(ConstClass(_ll_1_threadlocalref_get__INTLlT_Signed), 48, descr=<Calli 4 i EF=2 OS=5>)
            f162 = float_add(f157, 11235582092889474423308157442431404585112356118389416079589380072358292237843810195794279832650471001320007117491962084853674360550901038905802964414967132773610493339054092829768888725077880882465817684505312860552384417646403930092119569408801702322709406917786643639996702871154982269052209770601514008576.000000)
            i163 = float_eq(f162, f157)
            guard_false(i163, descr=<Guard0xa8d2020>)
            i164 = int_is_true(i160)
            guard_false(i164, descr=<Guard0xa75d220>)
            i165 = int_is_true(i139)
            guard_false(i165, descr=<Guard0xa75d268>)
            f167 = float_add(f157, 2.000000)
            i169 = int_add(i115, 1)
            i171 = int_sub(i119, 1)
            setfield_gc(ConstPtr(ptr172), i171, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
            i174 = int_le(i171, 0)
            guard_false(i174, descr=<Guard0xa8d2088>)
            i175 = arraylen_gc(p55, descr=<ArrayP 8>)
            jump(p0, p1, i2, p3, p4, p7, p8, p10, i129, i169, p23, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, p55, p57, i171, descr=TargetToken(175413136))
            """)
        else:
            self.assert_matches(traces[1].loop,
            """
            guard_not_invalidated(descr=<Guard0x94415f4>)
            i134 = int_le(i125, 1000000)
            guard_true(i134, descr=<Guard0x94d5ed4>)
            p135 = force_token()
            enter_portal_frame(4, 0)
            leave_portal_frame(4)
            p139 = force_token()
            enter_portal_frame(4, 0)
            leave_portal_frame(4)
            f144 = call_f(ConstClass(_ll_1_ullong_from_uint__Unsigned), i125, descr=<CallL 8 i EF=0 OS=93>)
            f147 = call_f(ConstClass(_ll_2_ullong_lshift__UnsignedLongLong_Signed), f144, 32, descr=<CallL 8 Li EF=0 OS=81>)
            f149 = call_f(ConstClass(_ll_2_ullong_or__UnsignedLongLong_UnsignedLongLong), f147, f144, descr=<CallL 8 LL EF=0 OS=80>)
            f152 = call_f(ConstClass(_ll_2_ullong_urshift__UnsignedLongLong_Signed), f149, 63, descr=<CallL 8 Li EF=0 OS=92>)
            i154 = call_i(ConstClass(_ll_1_llong_to_int__UnsignedLongLong), f152, descr=<Calli 4 L EF=0 OS=85>)
            f157 = call_f(ConstClass(_ll_2_ullong_and__UnsignedLongLong_UnsignedLongLong), f149, inf, descr=<CallL 8 LL EF=0 OS=79>)
            f160 = call_f(ConstClass(_ll_2_ullong_urshift__UnsignedLongLong_Signed), f157, 52, descr=<CallL 8 Li EF=0 OS=92>)
            i162 = call_i(ConstClass(_ll_1_llong_to_int__UnsignedLongLong), f160, descr=<Calli 4 L EF=0 OS=85>)
            f165 = call_f(ConstClass(_ll_2_ullong_and__UnsignedLongLong_UnsignedLongLong), f149, 0.000000, descr=<CallL 8 LL EF=0 OS=79>)
            guard_value(i162, 0, descr=<Guard0x9441628>)
            f169 = call_f(ConstClass(_ll_1_ullong_u_to_float__UnsignedLongLong), f165, descr=<Callf 8 L EF=0 OS=94>)
            i171 = float_eq(f169, 0.000000)
            guard_false(i171, descr=<Guard0x944165c>)
            f172 = float_sub(f169, f169)
            i174 = float_eq(f172, 0.000000)
            guard_true(i174, descr=<Guard0x94d5ef8>)
            f177 = call_f(ConstClass(ccall_ldexp), f169, -1074, descr=<Callf 8 fi EF=2>)
            i180 = call_i(ConstClass(_ll_1_threadlocalref_get__SignedLlT_Signed), 28, descr=<Calli 4 i EF=2 OS=5>)
            f182 = float_add(f177, 11235582092889474423308157442431404585112356118389416079589380072358292237843810195794279832650471001320007117491962084853674360550901038905802964414967132773610493339054092829768888725077880882465817684505312860552384417646403930092119569408801702322709406917786643639996702871154982269052209770601514008576.000000)
            i183 = float_eq(f182, f177)
            guard_false(i183, descr=<Guard0x9441690>)
            i184 = int_is_true(i180)
            guard_false(i184, descr=<Guard0x94d5f1c>)
            i185 = int_is_true(i154)
            guard_false(i185, descr=<Guard0x94d5f40>)
            f187 = float_add(f177, 2.000000)
            i189 = int_add(i125, 1)
            i191 = int_sub(i129, 1)
            setfield_gc(ConstPtr(ptr192), i191, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 32>)
            i194 = int_le(i191, 0)
            guard_false(i194, descr=<Guard0x94416c4>)
            i195 = arraylen_gc(p55, descr=<ArrayP 4>)
            jump(p0, p1, i2, p3, p4, p7, p8, p10, i125, i189, p23, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, p55, p57, i191, descr=TargetToken(155445900))
            """)

    def test_new_large_int(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | a |
        1 to: 1000000 do: [:i|
            a := Integer new: 8 neg: false.
            a := a + 2.
        ].
        """)
        if IS_64BIT:
            self.assert_matches(traces[0].loop,
            """
            guard_not_invalidated(descr=<Guard0xa8ca020>)
            i130 = int_le(i120, 1000000)
            guard_true(i130, descr=<Guard0xa8a8608>)
            p131 = force_token()
            enter_portal_frame(4, 0)
            p134 = force_token()
            enter_portal_frame(4, 0)
            leave_portal_frame(4)
            leave_portal_frame(4)
            p140 = new_array_clear(8, descr=<ArrayU 1>)
            p144 = call_r(ConstClass(frombytes), p140, ConstPtr(ptr142), 0, descr=<Callr 8 rri EF=4>)
            guard_no_exception(descr=<Guard0xa8ca088>)
            p147 = call_r(ConstClass(rbigint.add), p144, ConstPtr(ptr146), descr=<Callr 8 rr EF=4>)
            guard_no_exception(descr=<Guard0xa8ca0f0>)
            i148 = getfield_gc_i(p147, descr=<FieldS rpython.rlib.rbigint.rbigint.inst_sign 16 pure>)
            i150 = int_ge(i148, 0)
            guard_true(i150, descr=<Guard0xa8a86e0>)
            i151 = getfield_gc_i(p147, descr=<FieldS rpython.rlib.rbigint.rbigint.inst_size 24 pure>)
            i153 = int_le(i151, 2)
            guard_true(i153, descr=<Guard0xa8a8728>)
            i155 = call_i(ConstClass(rbigint._touint_helper), p147, descr=<Calli 8 r EF=4>)
            guard_no_exception(descr=<Guard0xa8ca158>)
            i157 = int_ge(i155, 0)
            guard_true(i157, descr=<Guard0xa8a8770>)
            i159 = int_add(i120, 1)
            i161 = int_sub(i124, 1)
            setfield_gc(ConstPtr(ptr162), i161, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
            i164 = int_le(i161, 0)
            guard_false(i164, descr=<Guard0xa8ca1c0>)
            i165 = arraylen_gc(p55, descr=<ArrayP 8>)
            i166 = arraylen_gc(p76, descr=<ArrayP 8>)
            jump(p0, p1, i2, p3, p4, p7, p8, p10, i155, i159, p23, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, p55, p57, p59, p76, p78, i161, descr=TargetToken(176747472))
            """)
        else:
            self.assert_matches(traces[0].loop,
            """
            guard_not_invalidated(descr=<Guard0x955a420>)
            i110 = int_le(i101, 1000000)
            guard_true(i110, descr=<Guard0x95c1ef8>)
            p111 = force_token()
            enter_portal_frame(4, 0)
            p114 = force_token()
            enter_portal_frame(4, 0)
            leave_portal_frame(4)
            leave_portal_frame(4)
            i120 = int_add(i101, 1)
            i122 = int_sub(i105, 1)
            setfield_gc(ConstPtr(ptr123), i122, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 32>)
            i125 = int_le(i122, 0)
            guard_false(i125, descr=<Guard0x955a454>)
            i127 = arraylen_gc(p55, descr=<ArrayP 4>)
            i128 = arraylen_gc(p76, descr=<ArrayP 4>)
            jump(p0, p1, i2, p3, p4, p7, p8, p10, i120, p23, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, p55, p57, p59, p76, p78, i122, descr=TargetToken(156580140))
            """)

    def test_large_negation0(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | a |
        a := 1 - (2 raisedTo: 128).
        1 to: 1000000 do: [:i|
            a negated.
        ].
        """)
        self.assert_matches(traces[0].loop,
        """
        guard_not_invalidated(descr=<Guard0xb8c9dc8>)
        i129 = int_le(i120, 1000000)
        guard_true(i129, descr=<Guard0xb8d6728>)
        p131 = getfield_gc_r(ConstPtr(ptr130), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p131, ConstPtr(ptr132), descr=<Guard0xb8c9e30>)
        p134 = getfield_gc_r(ConstPtr(ptr133), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p134, ConstPtr(ptr135), descr=<Guard0xb8c9e98>)
        p136 = force_token()
        enter_portal_frame(4, 0)
        p140 = getfield_gc_r(ConstPtr(ptr139), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p140, ConstPtr(ptr141), descr=<Guard0xb8c9f00>)
        p143 = getfield_gc_r(ConstPtr(ptr142), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst__storage 24>)
        p145 = getarrayitem_gc_r(p143, 1, descr=<ArrayP 8>)
        guard_nonnull_class(p145, ConstClass(W_PointersObject), descr=<Guard0xb8c9f68>)
        i146 = getfield_gc_i(p11, descr=<FieldS rsqueakvm.model.numeric.W_LargeIntegerBig.inst__exposed_size 40>)
        i148 = cond_call_value_i(i146, ConstClass(calculate_exposed_size_for_big_int), p69, descr=<Calli 8 r EF=4>)
        guard_no_exception(descr=<Guard0xba3a020>)
        p150 = getfield_gc_r(ConstPtr(ptr149), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        setfield_gc(p11, i148, descr=<FieldS rsqueakvm.model.numeric.W_LargeIntegerBig.inst__exposed_size 40>)
        guard_value(p150, ConstPtr(ptr151), descr=<Guard0xba3a088>)
        p152 = getfield_gc_r(p150, descr=<FieldP rsqueakvm.storage.AbstractCachingShadow.inst_version 32 pure>)
        guard_value(p152, ConstPtr(ptr153), descr=<Guard0xb8d6770>)
        p154 = getfield_gc_r(p145, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p154, ConstPtr(ptr155), descr=<Guard0xba3a0f0>)
        p156 = getfield_gc_r(p154, descr=<FieldP rsqueakvm.storage.AbstractStrategy.inst_w_class 8 pure>)
        guard_value(p156, ConstPtr(ptr157), descr=<Guard0xb8d67b8>)
        p159 = getfield_gc_r(ConstPtr(ptr158), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p159, ConstPtr(ptr160), descr=<Guard0xba3a158>)
        p161 = force_token()
        enter_portal_frame(4, 0)
        i165 = int_lt(i148, 0)
        guard_false(i165, descr=<Guard0xb8d6800>)
        p166 = new_array_clear(i148, descr=<ArrayU 1>)
        p168 = getfield_gc_r(ConstPtr(ptr167), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p168, ConstPtr(ptr169), descr=<Guard0xba3a1c0>)
        leave_portal_frame(4)
        p171 = force_token()
        enter_portal_frame(4, 0)
        p175 = getfield_gc_r(ConstPtr(ptr174), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p175, ConstPtr(ptr176), descr=<Guard0xba3a228>)
        p177 = force_token()
        enter_portal_frame(4, 0)
        leave_portal_frame(4)
        i182 = int_sub(i148, 1)
        i183 = int_le(i148, i182)
        guard_false(i183, descr=<Guard0xb8d6848>)
        p184 = force_token()
        p185 = new_with_vtable(descr=<SizeDescr 64>)
        p186 = new_with_vtable(descr=<SizeDescr 8>)
        setfield_gc(p185, ConstPtr(ptr187), descr=<FieldP rsqueakvm.model.base.W_AbstractObjectWithClassReference.inst_w_class 24 pure>)
        setfield_gc(p0, p184, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.vable_token 16>)
        setfield_gc(p185, 9223372036854775807, descr=<FieldS rsqueakvm.model.base.W_AbstractObjectWithIdentityHash.inst_hash 8 pure>)
        setfield_gc(p185, p166, descr=<FieldP rsqueakvm.model.variable.W_BytesObject.inst_bytes 40>)
        setfield_gc(p185, p186, descr=<FieldP rsqueakvm.model.variable.W_BytesObject.inst_version 48 pure>)
        call_may_force_n(ConstClass(_replace_from_to_trampoline__v77___simple_call__function__r), 0, i182, 0, p185, p13, descr=<Callv 0 iiirr EF=7>)
        guard_not_forced(descr=<Guard0xb8c1ad0>)
        guard_no_exception(descr=<Guard0xb8d6890>)
        guard_not_invalidated(descr=<Guard0xb8d68d8>)
        leave_portal_frame(4)
        leave_portal_frame(4)
        i195 = int_add(i120, 1)
        i197 = getfield_gc_i(ConstPtr(ptr196), descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        i199 = int_sub(i197, 1)
        setfield_gc(ConstPtr(ptr200), i199, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        i202 = int_le(i199, 0)
        guard_false(i202, descr=<Guard0xba3a290>)
        jump(p0, p1, i2, p3, p4, p7, p8, p10, p13, i195, p21, p23, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, descr=TargetToken(193745952))
        """)

    # This is a bit full, unfortunately, but there shouldn't be any BlockClosure accesses in this loop
    def test_interval_do(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | a b |
        a := 1 - (2 raisedTo: 128).
        (1 to: 1000000) do: [:i|
            b := a negated.
        ].
        """)
        self.assert_matches(traces[0].loop,
        """
        guard_not_invalidated(descr=<Guard0x4965f68>)
        i176 = int_lt(i66, i49)
        guard_true(i176, descr=<Guard0x6454848>)
        p177 = getfield_gc_r(p6, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 24>)
        guard_value(p177, ConstPtr(ptr178), descr=<Guard0x48e6020>)
        p179 = getfield_gc_r(p6, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst__storage 16>)
        i181 = getarrayitem_gc_i(p179, 0, descr=<ArrayS 8>)
        i183 = int_eq(i181, 9223372036854775807)
        guard_false(i183, descr=<Guard0x6454890>)
        i185 = getarrayitem_gc_i(p179, 2, descr=<ArrayS 8>)
        i187 = int_eq(i185, 9223372036854775807)
        guard_false(i187, descr=<Guard0x64548d8>)
        i188 = int_mul_ovf(i66, i185)
        guard_no_overflow(descr=<Guard0x6454920>)
        i189 = int_add_ovf(i181, i188)
        guard_no_overflow(descr=<Guard0x6454968>)
        i191 = int_add(i66, 1)
        p193 = getfield_gc_r(ConstPtr(ptr192), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 24>)
        guard_value(p193, ConstPtr(ptr194), descr=<Guard0x48e6088>)
        p196 = getarrayitem_gc_r(p77, 0, descr=<ArrayP 8>)
        guard_nonnull_class(p196, ConstClass(W_LargeIntegerBig), descr=<Guard0x48e6708>)
        p199 = getarrayitem_gc_r(p77, 1, descr=<ArrayP 8>)
        guard_nonnull_class(p199, ConstClass(W_PointersObject), descr=<Guard0x48e66a0>)
        p201 = force_token()
        enter_portal_frame(1, 0)
        p204 = getfield_gc_r(p196, descr=<FieldP rsqueakvm.model.base.W_AbstractObjectWithClassReference.inst_w_class 16 pure>)
        guard_value(p204, ConstPtr(ptr205), descr=<Guard0x6454c38>)
        p207 = getfield_gc_r(ConstPtr(ptr206), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 24>)
        guard_value(p207, ConstPtr(ptr208), descr=<Guard0x48e6638>)
        p209 = force_token()
        enter_portal_frame(1, 0)
        p213 = getfield_gc_r(ConstPtr(ptr212), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 24>)
        guard_value(p213, ConstPtr(ptr214), descr=<Guard0x48e65d0>)
        p216 = getfield_gc_r(ConstPtr(ptr215), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst__storage 16>)
        p218 = getarrayitem_gc_r(p216, 1, descr=<ArrayP 8>)
        guard_nonnull_class(p218, ConstClass(W_PointersObject), descr=<Guard0x48e6568>)
        i220 = getfield_gc_i(p196, descr=<FieldS rsqueakvm.model.numeric.W_LargeIntegerBig.inst__exposed_size 32>)
        p221 = getfield_gc_r(p196, descr=<FieldP rsqueakvm.model.numeric.W_LargeIntegerBig.inst_value 40 pure>)
        i223 = cond_call_value_i(i220, ConstClass(calculate_exposed_size_for_big_int), p221, descr=<Calli 8 r EF=4>)
        guard_no_exception(descr=<Guard0x48e6498>)
        p225 = getfield_gc_r(ConstPtr(ptr224), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 24>)
        setfield_gc(p196, i223, descr=<FieldS rsqueakvm.model.numeric.W_LargeIntegerBig.inst__exposed_size 32>)
        guard_value(p225, ConstPtr(ptr226), descr=<Guard0x48e6430>)
        p227 = getfield_gc_r(p225, descr=<FieldP rsqueakvm.storage.AbstractCachingShadow.inst_version 32 pure>)
        guard_value(p227, ConstPtr(ptr228), descr=<Guard0x6454ba8>)
        p229 = getfield_gc_r(p218, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 24>)
        guard_value(p229, ConstPtr(ptr230), descr=<Guard0x48e63c8>)
        p231 = getfield_gc_r(p229, descr=<FieldP rsqueakvm.storage.AbstractStrategy.inst_w_class 8 pure>)
        guard_value(p231, ConstPtr(ptr232), descr=<Guard0x6454b60>)
        p234 = getfield_gc_r(ConstPtr(ptr233), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 24>)
        guard_value(p234, ConstPtr(ptr235), descr=<Guard0x48e6360>)
        p236 = force_token()
        enter_portal_frame(1, 0)
        i240 = int_lt(i223, 0)
        guard_false(i240, descr=<Guard0x6454b18>)
        p241 = new_array_clear(i223, descr=<ArrayU 1>)
        p243 = getfield_gc_r(ConstPtr(ptr242), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 24>)
        guard_value(p243, ConstPtr(ptr244), descr=<Guard0x48e62f8>)
        leave_portal_frame(1)
        p246 = force_token()
        enter_portal_frame(1, 0)
        p250 = getfield_gc_r(ConstPtr(ptr249), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 24>)
        guard_value(p250, ConstPtr(ptr251), descr=<Guard0x48e6290>)
        p252 = force_token()
        enter_portal_frame(1, 0)
        leave_portal_frame(1)
        i257 = int_sub(i223, 1)
        i258 = int_le(i223, i257)
        guard_false(i258, descr=<Guard0x6454ad0>)
        p259 = force_token()
        p260 = new_with_vtable(descr=<SizeDescr 56>)
        p261 = new_with_vtable(descr=<SizeDescr 8>)
        setfield_gc(p260, p261, descr=<FieldP rsqueakvm.model.variable.W_BytesObject.inst_version 40 pure>)
        setfield_gc(p260, ConstPtr(ptr262), descr=<FieldP rsqueakvm.model.base.W_AbstractObjectWithClassReference.inst_w_class 16 pure>)
        setfield_gc(p0, p259, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.vable_token 16>)
        setfield_gc(p260, 0, descr=<FieldS rsqueakvm.model.base.W_AbstractObjectWithIdentityHash.inst_hash 8>)
        setfield_gc(p260, p241, descr=<FieldP rsqueakvm.model.variable.W_BytesObject.inst_bytes 32>)
        call_may_force_n(ConstClass(_replace_from_to_trampoline__v124___simple_call__function__), 0, i257, 0, p260, p196, descr=<Callv 0 iiirr EF=7>)
        guard_not_forced(descr=<Guard0x63ea4f0>)
        guard_no_exception(descr=<Guard0x6454a88>)
        guard_not_invalidated(descr=<Guard0x6454a40>)
        leave_portal_frame(1)
        leave_portal_frame(1)
        p269 = getfield_gc_r(p199, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 24>)
        guard_value(p269, ConstPtr(ptr270), descr=<Guard0x48e61c0>)
        p272 = getfield_gc_r(ConstPtr(ptr271), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 24>)
        guard_value(p272, ConstPtr(ptr273), descr=<Guard0x48e6158>)
        p274 = getfield_gc_r(p199, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst__storage 16>)
        leave_portal_frame(1)
        i277 = getfield_gc_i(ConstPtr(ptr276), descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        i279 = int_sub(i277, 1)
        setfield_gc(ConstPtr(ptr280), i279, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        setarrayitem_gc(p274, 0, p260, descr=<ArrayP 8>)
        i283 = int_le(i279, 0)
        guard_false(i283, descr=<Guard0x48e60f0>)
        jump(p0, p1, i2, p4, p5, p6, p8, p11, i189, i191, p17, p260, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, i49, p77, p72, descr=TargetToken(104558688))
        """)

    def test_dnu(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | c i |
        Object
            subclass: #MyA
            instanceVariableNames: ''
            classVariableNames: ''
            poolDictionaries: ''
            category: 'Test'.
        c := Smalltalk at: #MyA  .
        c compile: 'doesNotUnderstand: aMessage
        ^ {aMessage selector. aMessage arguments. aMessage lookupClass}' classified: 'none' withStamp: nil notifying: nil logSource: false.

        i := c new.
        1 to: 100000 do: [:ignored | i foo ]
        """)
        self.assert_matches(traces[-1].loop, """
        guard_not_invalidated(descr=<Guard0x9facdf0>)
        i77 = int_le(i68, 100000)
        guard_true(i77, descr=<Guard0x9f9cb60>)
        p78 = force_token()
        enter_portal_frame(4, 0)
        leave_portal_frame(4)
        i83 = int_add(i68, 1)
        i85 = int_sub(i72, 1)
        setfield_gc(ConstPtr(ptr86), i85, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        i88 = int_le(i85, 0)
        guard_false(i88, descr=<Guard0x9facd88>)
        jump(p0, p1, i2, p4, p5, p6, p8, p11, p13, i83, p21, p23, p25, p27, p29, p31, p33, p35, p37, p39, p41, i85, descr=TargetToken(166460720))
        """)

    def test_oam(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | c i |
        Object
            subclass: #MyOaM
            instanceVariableNames: ''
            classVariableNames: ''
            poolDictionaries: ''
            category: 'Test'.
        c := Smalltalk at: #MyOaM.
        c compile: 'run: aSelector with: someArgs in: aReceiver
        ^ {aSelector. someArgs. aReceiver}' classified: 'none' withStamp: nil notifying: nil logSource: false.

        Object
            subclass: #MyA
            instanceVariableNames: ''
            classVariableNames: ''
            poolDictionaries: ''
            category: 'Test'.
        c := Smalltalk at: #MyA.
        c methodDict at: #oam put: (Smalltalk at: #MyOaM) new.
        i := c new.
        1 to: 100000 do: [:ignored | i oam ]
        """)
        self.assert_matches(traces[-1].loop, """
        guard_not_invalidated(descr=<Guard0xafaeff8>)
        i80 = int_le(i71, 100000)
        guard_true(i80, descr=<Guard0xaea95c8>)
        p81 = force_token()
        enter_portal_frame(4, 0)
        leave_portal_frame(4)
        i86 = int_add(i71, 1)
        i88 = int_sub(i75, 1)
        setfield_gc(ConstPtr(ptr89), i88, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        i91 = int_le(i88, 0)
        guard_false(i91, descr=<Guard0xafaf060>)
        jump(p0, p1, i2, p4, p5, p6, p8, p11, p13, i86, p21, p23, p25, p27, p29, p31, p33, p35, p37, p39, p41, i88, descr=TargetToken(184206704))
        """)

    def test_literal_array(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | c i |
        Object
            subclass: #MyA
            instanceVariableNames: ''
            classVariableNames: ''
            poolDictionaries: ''
            category: 'Test'.
        c := Smalltalk at: #MyA.
        c compile: 'newLiteralArray
        ^ {$c. 1. 12.0. self}' classified: 'none' withStamp: nil notifying: nil logSource: false.
        i := c new.
        1 to: 100000 do: [:ignored | i newLiteralArray ]
        """)
        self.assert_matches(traces[-1].loop, """
        guard_not_invalidated(descr=<Guard0xb605748>)
        i74 = int_le(i65, 100000)
        guard_true(i74, descr=<Guard0xb608608>)
        p75 = force_token()
        enter_portal_frame(4, 0)
        leave_portal_frame(4)
        i80 = int_add(i65, 1)
        i82 = int_sub(i69, 1)
        setfield_gc(ConstPtr(ptr83), i82, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        i85 = int_le(i82, 0)
        guard_false(i85, descr=<Guard0xb6057b0>)
        jump(p0, p1, i2, p4, p5, p6, p8, p11, p13, i80, p21, p23, p25, p27, p29, p31, p33, p35, p37, p39, p41, i82, descr=TargetToken(189806080))
        """)

    def test_identity_hash_known_object(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | c |
        Object
            subclass: #MyA
            instanceVariableNames: ''
            classVariableNames: ''
            poolDictionaries: ''
            category: 'Test'.
        c := (Smalltalk at: #MyA) new.
        1 to: 10000 do: [:i | c identityHash ].
        """)
        # important: there shouldn't be a getfield inst_hash before the cond_call to calculate the hash
        self.assert_matches(traces[-1].loop, """
        guard_not_invalidated(descr=<Guard0x36c5880>)
        i67 = int_le(i58, 10000)
        guard_true(i67, descr=<Guard0x3de4ec0>)
        i69 = cond_call_value_i(i54, ConstClass(calculate_and_cache), p11, descr=<Calli 8 r EF=5>)
        guard_no_exception(descr=<Guard0x36c58e8>)
        guard_not_invalidated(descr=<Guard0x3de4f08>)
        i71 = int_add(i58, 1)
        i73 = int_sub(i62, 1)
        setfield_gc(ConstPtr(ptr74), i73, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        i76 = int_le(i73, 0)
        guard_false(i76, descr=<Guard0x36c5950>)
        jump(p0, p1, i2, p4, p5, p6, p8, p11, i71, p19, p21, p23, p25, p27, p29, p31, p33, p35, p37, p39, p41, i54, i73, descr=TargetToken(86285936))
        """)

    def test_identity_hash_fresh_object(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        | c coll s |
        Object
            subclass: #MyA
            instanceVariableNames: ''
            classVariableNames: ''
            poolDictionaries: ''
            category: 'Test'.
        c := Smalltalk at: #MyA.
        coll := OrderedCollection new.
        1 to: 10000 do: [:ignored | coll add: c new].
        1 to: 10000 do: [:i | (coll at: i) identityHash ].
        """)
        # important: there shouldn't be a setfield inst_hash or an abort, just a getfield for the hash value and a cond_call
        self.assert_matches(traces[-1].loop, """
        guard_not_invalidated(descr=<Guard0x3addaf0>)
        i116 = int_le(i107, 10000)
        guard_true(i116, descr=<Guard0x3c28a88>)
        p117 = force_token()
        enter_portal_frame(1, 0)
        i120 = int_add_ovf(i107, i71)
        guard_no_overflow(descr=<Guard0x3c28a40>)
        i122 = int_sub(i120, 1)
        i123 = int_gt(i122, i78)
        guard_false(i123, descr=<Guard0x3c289f8>)
        i125 = int_sub(i122, 1)
        i126 = uint_lt(i125, i91)
        guard_true(i126, descr=<Guard0x3c289b0>)
        i128 = int_lt(i125, 0)
        guard_false(i128, descr=<Guard0x3c28968>)
        p129 = getarrayitem_gc_r(p90, i125, descr=<ArrayP 8>)
        guard_nonnull_class(p129, ConstClass(W_PointersObject), descr=<Guard0x3adda88>)
        leave_portal_frame(1)
        p132 = getfield_gc_r(p129, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p132, ConstPtr(ptr133), descr=<Guard0x3add9b8>)
        i134 = getfield_gc_i(p129, descr=<FieldS rsqueakvm.model.base.W_AbstractObjectWithIdentityHash.inst_hash 8 pure>)
        i136 = cond_call_value_i(i134, ConstClass(calculate_and_cache), p129, descr=<Calli 8 r EF=5>)
        guard_no_exception(descr=<Guard0x3add8e8>)
        guard_not_invalidated(descr=<Guard0x3c288d8>)
        i138 = int_add(i107, 1)
        i140 = int_sub(i111, 1)
        setfield_gc(ConstPtr(ptr141), i140, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        i143 = int_le(i140, 0)
        guard_false(i143, descr=<Guard0x3add880>)
        i145 = arraylen_gc(p67, descr=<ArrayP 8>)
        jump(p0, p1, i2, p4, p5, p6, p8, p11, p13, p15, p17, i138, p25, p27, p29, p31, p33, p35, p37, p39, p41, p67, p69, i71, p76, i78, p81, i91, p90, i140, descr=TargetToken(90449984))
        """)

    def test_nested_closure_loop_call(self, spy, tmpdir):
        traces = self.run(spy, tmpdir, """
        1 to: 2000 do: [:a |
            (1 to: 1000) do: [:b |
                b abs.
            ]
        ].
        """)
        # important: there should be two loops, with the outer calling the inner, and in between an entry bridge to the inner loop abs call
        self.assert_matches(traces[-3].loop, """
        guard_not_invalidated(descr=<Guard0x4f86cb8>)
        i106 = int_lt(i66, i49)
        guard_true(i106, descr=<Guard0x6a78f98>)
        i107 = int_mul_ovf(i66, i60)
        guard_no_overflow(descr=<Guard0x6a78f50>)
        i108 = int_add_ovf(i56, i107)
        guard_no_overflow(descr=<Guard0x6a78ec0>)
        i110 = int_add(i66, 1)
        p111 = force_token()
        enter_portal_frame(1, 0)
        p114 = force_token()
        enter_portal_frame(1, 0)
        i118 = int_lt(i108, 0)
        guard_false(i118, descr=<Guard0x6a79070>)
        leave_portal_frame(1)
        leave_portal_frame(1)
        i122 = int_sub(i102, 1)
        setfield_gc(ConstPtr(ptr123), i122, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        i125 = int_le(i122, 0)
        guard_false(i125, descr=<Guard0x4f87198>)
        i127 = arraylen_gc(p54, descr=<ArrayS 8>)
        jump(p0, p1, i2, p4, p5, p6, p8, p11, i108, i110, p17, p25, p27, p29, p31, p33, p35, p37, p39, p41, p43, i49, p54, i60, i56, i122, descr=TargetToken(111727328))
        """)
        assert len(traces[-2].setup) > 0
        self.assert_matches(traces[-1].loop, """
        guard_not_invalidated(descr=<Guard0x3db9268>)
        i212 = int_le(i203, 2000)
        guard_true(i212, descr=<Guard0x5929c88>)
        p214 = getfield_gc_r(ConstPtr(ptr213), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p214, ConstPtr(ptr215), descr=<Guard0x3db9610>)
        p217 = getfield_gc_r(ConstPtr(ptr216), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p217, ConstPtr(ptr218), descr=<Guard0x3db95a8>)
        p219 = force_token()
        enter_portal_frame(1, 0)
        p223 = getfield_gc_r(ConstPtr(ptr222), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p223, ConstPtr(ptr224), descr=<Guard0x3db9540>)
        p226 = getfield_gc_r(ConstPtr(ptr225), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst__storage 24>)
        p228 = getarrayitem_gc_r(p226, 1, descr=<ArrayP 8>)
        guard_nonnull_class(p228, ConstClass(W_PointersObject), descr=<Guard0x3db94d8>)
        p230 = getfield_gc_r(p228, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p230, ConstPtr(ptr231), descr=<Guard0x3db9470>)
        p232 = getfield_gc_r(p230, descr=<FieldP rsqueakvm.storage.AbstractStrategy.inst_w_class 8 pure>)
        guard_value(p232, ConstPtr(ptr233), descr=<Guard0x5929c40>)
        p235 = getfield_gc_r(ConstPtr(ptr234), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p235, ConstPtr(ptr236), descr=<Guard0x3db9408>)
        p237 = force_token()
        enter_portal_frame(1, 0)
        p241 = getfield_gc_r(ConstPtr(ptr240), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p241, ConstPtr(ptr242), descr=<Guard0x3db93a0>)
        p243 = getfield_gc_r(p241, descr=<FieldP rsqueakvm.storage.AbstractCachingShadow.inst_version 32 pure>)
        guard_value(p243, ConstPtr(ptr244), descr=<Guard0x5929bf8>)
        p246 = getfield_gc_r(ConstPtr(ptr245), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_value(p246, ConstPtr(ptr247), descr=<Guard0x3db9338>)
        p248 = force_token()
        enter_portal_frame(1, 0)
        leave_portal_frame(1)
        leave_portal_frame(1)
        leave_portal_frame(1)
        p254 = getfield_gc_r(p1, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        guard_nonnull_class(p254, ConstClass(ContextPartShadow), descr=<Guard0x3db92d0>)
        i256 = ptr_eq(p254, p0)
        guard_true(i256, descr=<Guard0x5929b68>)
        p257 = force_token()
        enter_portal_frame(1, 0)
        p260 = force_token()
        enter_portal_frame(1, 0)
        leave_portal_frame(1)
        p264 = force_token()
        enter_portal_frame(1, 0)
        p267 = force_token()
        enter_portal_frame(1, 0)
        leave_portal_frame(1)
        leave_portal_frame(1)
        i273 = int_sub(i207, 1)
        setfield_gc(ConstPtr(ptr274), i273, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        i276 = int_le(i273, 0)
        guard_false(i276, descr=<Guard0x3db9198>)
        p277 = force_token()
        p278 = new_with_vtable(descr=<SizeDescr 96>)
        p279 = new_with_vtable(descr=<SizeDescr 24>)
        setfield_gc(p279, p257, descr=<FieldP JitVirtualRef.virtual_token 8>)
        setfield_gc(p279, ConstPtr(null), descr=<FieldP JitVirtualRef.forced 16>)
        p281 = new_array_clear(17, descr=<ArrayP 8>)
        p282 = new_with_vtable(descr=<SizeDescr 88>)
        setfield_gc(p282, 0, descr=<FieldS rsqueakvm.model.base.W_AbstractObjectWithIdentityHash.inst_hash 8 pure>)
        setfield_gc(p282, 1, descr=<FieldS rsqueakvm.model.block_closure.W_BlockClosure.inst__numArgs 24 pure>)
        setfield_gc(p282, ConstPtr(ptr285), descr=<FieldP rsqueakvm.model.block_closure.W_BlockClosure.inst__stack 32 pure>)
        setfield_gc(p282, 47, descr=<FieldS rsqueakvm.model.block_closure.W_BlockClosure.inst__startpc 40 pure>)
        setfield_gc(p282, ConstPtr(ptr287), descr=<FieldP rsqueakvm.model.block_closure.W_BlockClosure.inst__w_method 48 pure>)
        setfield_gc(p282, p1, descr=<FieldP rsqueakvm.model.block_closure.W_BlockClosure.inst__w_outerContext 56 pure>)
        setfield_gc(p282, p6, descr=<FieldP rsqueakvm.model.block_closure.W_BlockClosure.inst__w_receiver 64 pure>)
        setfield_gc(p282, ConstPtr(ptr288), descr=<FieldP rsqueakvm.model.block_closure.W_BlockClosure.inst_version 72 pure>)
        setarrayitem_gc(p281, 0, p282, descr=<ArrayP 8>)
        p290 = new_with_vtable(descr=<SizeDescr 16>)
        setfield_gc(p290, 1, descr=<FieldS rsqueakvm.model.numeric.W_SmallInteger.inst_value 8 pure>)
        setarrayitem_gc(p281, 1, p290, descr=<ArrayP 8>)
        p293 = new_with_vtable(descr=<SizeDescr 16>)
        setfield_gc(p293, 1, descr=<FieldS rsqueakvm.model.numeric.W_SmallInteger.inst_value 8 pure>)
        setarrayitem_gc(p281, 2, p293, descr=<ArrayP 8>)
        p296 = new_with_vtable(descr=<SizeDescr 16>)
        setfield_gc(p296, 1000, descr=<FieldS rsqueakvm.model.numeric.W_SmallInteger.inst_value 8 pure>)
        setarrayitem_gc(p281, 3, p296, descr=<ArrayP 8>)
        p299 = new_with_vtable(descr=<SizeDescr 16>)
        setfield_gc(p299, 1, descr=<FieldS rsqueakvm.model.numeric.W_SmallInteger.inst_value 8 pure>)
        setarrayitem_gc(p281, 4, p299, descr=<ArrayP 8>)
        setarrayitem_gc(p281, 5, ConstPtr(ptr303), descr=<ArrayP 8>)
        setarrayitem_gc(p281, 6, ConstPtr(ptr305), descr=<ArrayP 8>)
        setarrayitem_gc(p281, 7, ConstPtr(ptr307), descr=<ArrayP 8>)
        setarrayitem_gc(p281, 8, ConstPtr(ptr309), descr=<ArrayP 8>)
        setarrayitem_gc(p281, 9, ConstPtr(ptr311), descr=<ArrayP 8>)
        setarrayitem_gc(p281, 10, ConstPtr(ptr313), descr=<ArrayP 8>)
        setarrayitem_gc(p281, 11, ConstPtr(ptr315), descr=<ArrayP 8>)
        setarrayitem_gc(p281, 12, ConstPtr(ptr317), descr=<ArrayP 8>)
        setarrayitem_gc(p281, 13, ConstPtr(ptr319), descr=<ArrayP 8>)
        setarrayitem_gc(p281, 14, ConstPtr(ptr321), descr=<ArrayP 8>)
        setarrayitem_gc(p281, 15, ConstPtr(ptr323), descr=<ArrayP 8>)
        setarrayitem_gc(p281, 16, ConstPtr(ptr325), descr=<ArrayP 8>)
        p326 = new_with_vtable(descr=<SizeDescr 40>)
        setfield_gc(p326, 0, descr=<FieldS rsqueakvm.model.base.W_AbstractObjectWithIdentityHash.inst_hash 8 pure>)
        p329 = new_array(3, descr=<ArrayS 8>)
        setarrayitem_gc(p329, 0, 1, descr=<ArrayS 8>)
        setarrayitem_gc(p329, 1, 1000, descr=<ArrayS 8>)
        setarrayitem_gc(p329, 2, 1, descr=<ArrayS 8>)
        setfield_gc(p326, p329, descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst__storage 24>)
        setfield_gc(p326, ConstPtr(ptr336), descr=<FieldP rsqueakvm.model.pointers.W_PointersObject.inst_strategy 32>)
        setfield_gc(p278, ConstPtr(ptr337), descr=<FieldP rsqueakvm.storage.AbstractStrategy.inst_w_class 8 pure>)
        setfield_gc(p0, p277, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.vable_token 16>)
        setfield_gc(p278, p279, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__s_sender 24>)
        setfield_gc(p278, 1090519045, descr=<FieldU rsqueakvm.storage_contexts.ContextPartShadow.inst__state_stackptr_pc 32>)
        setfield_gc(p278, p281, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__temps_and_stack 40>)
        setfield_gc(p278, ConstPtr(ptr339), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__w_method 48>)
        setfield_gc(p278, p326, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__w_receiver 56>)
        setfield_gc(p278, ConstPtr(null), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__w_self 64>)
        setfield_gc(p278, 23, descr=<FieldS rsqueakvm.storage_contexts.ContextPartShadow.inst__w_self_size 72>)
        setfield_gc(p278, ConstPtr(null), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_closure 80>)
        setfield_gc(p278, ConstPtr(null), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_extra_data 88>)
        call_assembler_n(p278, descr=<Loop2>)
        guard_not_forced(descr=<Guard0x8c514b0>)
        keepalive(p278)
        p345 = guard_exception(13592624, descr=<Guard0x3db90c8>)
        i346 = ptr_eq(p278, p0)
        guard_false(i346, descr=<Guard0x3db9130>)
        p347 = getfield_gc_r(p278, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.vable_token 16>)
        i349 = ptr_ne(p347, ConstPtr(null))
        cond_call(i349, 6397552, p278, descr=<Callv 0 r EF=2 OS=121>)
        i351 = getfield_gc_i(p278, descr=<FieldU rsqueakvm.storage_contexts.ContextPartShadow.inst__state_stackptr_pc 32>)
        guard_value(i351, 1090519067, descr=<Guard0x3db8f28>)
        guard_not_invalidated(descr=<Guard0x5929da8>)
        p353 = getfield_gc_r(p278, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst_closure 80>)
        guard_isnull(p353, descr=<Guard0x5929df0>)
        p354 = getfield_gc_r(p278, descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__w_method 48>)
        guard_value(p354, ConstPtr(ptr355), descr=<Guard0x3db9b58>)
        setfield_gc(p278, ConstPtr(null), descr=<FieldP rsqueakvm.storage_contexts.ContextPartShadow.inst__s_sender 24>)
        setfield_gc(p278, 1094713343, descr=<FieldU rsqueakvm.storage_contexts.ContextPartShadow.inst__state_stackptr_pc 32>)
        guard_class(p345, 13592624, descr=<Guard0x3db9bc0>)
        p359 = getfield_gc_r(p345, descr=<FieldP rsqueakvm.interpreter.WrappedLocalReturn.inst_w_value 8 pure>)
        setfield_gc(p278, 20971519, descr=<FieldU rsqueakvm.storage_contexts.ContextPartShadow.inst__state_stackptr_pc 32>)
        setfield_gc(p279, ConstPtr(null), descr=<FieldP JitVirtualRef.virtual_token 8>)
        guard_nonnull(p359, descr=<Guard0x3db9c28>)
        i362 = int_add(i203, 1)
        i364 = getfield_gc_i(ConstPtr(ptr363), descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        i366 = int_sub(i364, 1)
        setfield_gc(ConstPtr(ptr367), i366, descr=<FieldS rsqueakvm.interpreter.Interpreter.inst_interrupt_check_counter 24>)
        i369 = int_le(i366, 0)
        guard_false(i369, descr=<Guard0x3db9c90>)
        jump(p0, p1, i2, p4, p5, p6, p8, i362, p17, p19, p21, p23, p25, p27, p29, p31, p33, p35, p37, p39, p41, i366, descr=TargetToken(92840368))
        """)
