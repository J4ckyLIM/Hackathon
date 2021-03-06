## Copyright 2019-2020 Smart Chain Arena LLC. ##

from browser import alert, window

import traceback
import inspect
import sys
import datetime
from types import FunctionType

pyRange = range
pyBool = bool
pyInt = int
pySet = set
pyList = list
pyTuple = tuple
pyBytes = bytes
pyMap = map

pyLen = len


def get_line_no():
    if window.in_browser:
        for x in reversed(getattr(inspect.currentframe(), "$stack")):
            line_info = getattr(x[1], "$line_info")
            if "exec" in line_info:
                return pyInt(line_info.split(",")[0])
        return -1
    else:
        for x in inspect.stack():
            if x.filename == "SmartPy Script":
                return x.lineno
        return -1


class Expr:
    def __init__(self, f, l):
        self._f = f
        self._l = l
        self.onUpdateHandlers = []
        self.attributes = {}
        self.opens = {}
        setattr(self, "__initialized", True)

    def __eq__(self, other):
        return Expr("eq", [self, spExpr(other), get_line_no()])

    def __ne__(self, other):
        return Expr("neq", [self, spExpr(other), get_line_no()])

    def __add__(self, other):
        return Expr("add", [self, spExpr(other), get_line_no()])

    def __sub__(self, other):
        return Expr("sub", [self, spExpr(other), get_line_no()])

    def __mul__(self, other):
        return Expr("mul", [self, spExpr(other), get_line_no()])

    def __mod__(self, other):
        return Expr("mod", [self, spExpr(other), get_line_no()])

    def __truediv__(self, other):
        return Expr("truediv", [self, spExpr(other), get_line_no()])

    def __floordiv__(self, other):
        return Expr("floordiv", [self, spExpr(other), get_line_no()])

    def __rtruediv__(self, other):
        return Expr("truediv", [spExpr(other), self, get_line_no()])

    def __rfloordiv__(self, other):
        return Expr("floordiv", [spExpr(other), self, get_line_no()])

    def __radd__(self, other):
        return Expr("add", [spExpr(other), self, get_line_no()])

    def __rmul__(self, other):
        return Expr("mul", [spExpr(other), self, get_line_no()])

    def __rsub__(self, other):
        return Expr("sub", [spExpr(other), self, get_line_no()])

    def __lt__(self, other):
        return Expr("lt", [self, spExpr(other), get_line_no()])

    def __le__(self, other):
        return Expr("le", [self, spExpr(other), get_line_no()])

    def __gt__(self, other):
        return Expr("gt", [self, spExpr(other), get_line_no()])

    def __ge__(self, other):
        return Expr("ge", [self, spExpr(other), get_line_no()])

    def __or__(self, other):
        return Expr("or", [self, spExpr(other), get_line_no()])

    def __ror__(self, other):
        return Expr("or", [spExpr(other), self, get_line_no()])

    def __xor__(self, other):
        return Expr("xor", [self, spExpr(other), get_line_no()])

    def __rxor__(self, other):
        return Expr("xor", [self, spExpr(other), get_line_no()])

    def __and__(self, other):
        return Expr("and", [self, spExpr(other), get_line_no()])

    def __rand__(self, other):
        return Expr("and", [spExpr(other), self, get_line_no()])

    def __lshift__(self, other):
        return Expr("lshift", [self, spExpr(other), get_line_no()])

    def __rlshift__(self, other):
        return Expr("lshift", [spExpr(other), self, get_line_no()])

    def __rshift__(self, other):
        return Expr("rshift", [self, spExpr(other), get_line_no()])

    def __rrshift__(self, other):
        return Expr("rshift", [spExpr(other), self, get_line_no()])

    def __getitem__(self, item):
        return Expr("getItem", [self, spExpr(item), get_line_no()])

    def __abs__(self):
        return Expr("abs", [self, get_line_no()])

    def __neg__(self):
        return Expr("neg", [self, get_line_no()])

    def __invert__(self):
        return Expr("invert", [self, get_line_no()])

    def __bool__(self):
        self.__nonzero__()

    def __nonzero__(self):
        raise Exception(
            "Cannot convert expression to bool. Conditionals are forbidden on contract expressions. Please use ~ or sp.if instead of not or if."
        )

    def __hash__(self):
        return hash(self.export())

    def on_update(self, f):
        self.onUpdateHandlers.append(f)

    def get(self, item, default_value = None, message = None):
        if default_value is not None:
            return Expr("getItemDefault", [self, spExpr(item), spExpr(default_value), get_line_no()])
        if message is not None:
            return Expr("getItemMessage", [self, spExpr(item), spExpr(message), get_line_no()])
        return self.__getitem__(item)

    def __enter__(self):
        return getattr(self, "__asBlock").__enter__()

    def __exit__(self, type, value, traceback):
        getattr(self, "__asBlock").__exit__(type, value, traceback)

    def __iter__(self):
        raise Exception(
            "Please use [sp.for var in expr] or [expr.items()] to iterate on a SmartPy expression."
        )

    def contains(self, value):
        return Expr("contains", [self, spExpr(value), get_line_no()])

    def __contains__(self, value):
        raise Exception(
            "Instead of using expressions such as e1 in e2, please use e2.contains(e1)."
        )

    def __call__(self, arg):
        return Expr("call_lambda", [self, spExpr(arg), get_line_no()])

    def apply(self, arg):
        return Expr("apply_lambda", [self, spExpr(arg), get_line_no()])

    def __getattr__(self, attr):
        if "__" in attr:
            raise AttributeError("")
        try:
            return self.attributes[attr]
        except KeyError:
            result = Expr("attr", [self, attr, get_line_no()])
            self.attributes[attr] = result
            return result

    def __setattr__(self, attr, value):
        if "__" not in attr and hasattr(self, "__initialized"):
            sp.set(getattr(self, attr), value)
            if (
                hasattr(getattr(self, attr), "onUpdateHandlers")
                and getattr(self, attr).onUpdateHandlers
            ):
                for f in getattr(self, attr).onUpdateHandlers:
                    f(getattr(self, attr), value)
        else:
            object.__setattr__(self, attr, value)


    def __delitem__(self, item):
        sp.delItem(self, item)

    def __setitem__(self, item, value):
        sp.set(self[item], value)

    def items(self):
        return Expr("items", [self, get_line_no()])

    def keys(self):
        return Expr("keys", [self, get_line_no()])

    def values(self):
        return Expr("values", [self, get_line_no()])

    def elements(self):
        return Expr("elements", [self, get_line_no()])

    def rev(self):
        return Expr("rev", [self, get_line_no()])

    def rev_items(self):
        return Expr("rev_items", [self, get_line_no()])

    def rev_keys(self):
        return Expr("rev_keys", [self, get_line_no()])

    def rev_values(self):
        return Expr("rev_values", [self, get_line_no()])

    def rev_elements(self):
        return Expr("rev_elements", [self, get_line_no()])

    def set(self, other):
        sp.set(self, spExpr(other))

    def add(self, item):
        sp.updateSet(self, item, True)

    def remove(self, item):
        sp.updateSet(self, item, False)

    def __repr__(self):
        return self.export()

    def match(self, constructor, argName="arg"):
        b = CommandBlock(sp)
        sp.newCommand(Expr("match", [self, constructor, argName, b, get_line_no()]))
        b.value = Expr("variant_arg", [argName, get_line_no()])
        b.value.__asBlock = b
        return b

    def match_cases(self, arg = None):
        b = CommandBlock(sp)
        if arg is None:
            arg = "match_%i" % (get_line_no())
        sp.newCommand(Expr("match_cases", [self, arg, b, get_line_no()]))
        b.value = Expr("cases_arg", [arg, get_line_no()])
        b.value.__asBlock = b
        return b

    def is_some(self):
        return self.is_variant("Some")

    def is_left(self):
        return self.is_variant("Left")

    def is_right(self):
        return self.is_variant("Right")

    def is_variant(self, name):
        return Expr("isVariant", [self, name, get_line_no()])

    def open_some(self, message = None):
        return self.open_variant("Some", message)

    def open_variant(self, name, message = None):
        if message is None:
            try:
                return self.opens[name]
            except KeyError:
                result = Expr("openVariant", [self, name, "None" if message is None else spExpr(message), get_line_no()])
                self.opens[name] = result
                return result
        else:
            return Expr("openVariant", [self, name, "None" if message is None else spExpr(message), get_line_no()])

    def append(self, other):
        raise Exception(
            "myList.append(..) is deprecated. Please use myList.push(..).\nBeware: push adds the element in front of the list (as in Michelson)."
        )

    def push(self, other):
        return sp.set(self, sp.cons(spExpr(other), self))

    def map(self, f):
        return Expr("map_function", [self, spExpr(f), get_line_no()])

    def verify_update(self, transition):
        return Expr("sapling_verify_update", [self, spExpr(transition), get_line_no()])

    def add_seconds(self, seconds):
        return Expr("add_seconds", [self, spExpr(seconds), get_line_no()])

    def add_minutes(self, minutes):
        return Expr("add_seconds", [self, spExpr(minutes * 60), get_line_no()])

    def add_hours(self, hours):
        return Expr("add_seconds", [self, spExpr(hours * 60 * 60), get_line_no()])

    def add_days(self, days):
        return Expr("add_seconds", [self, spExpr(days * 24 * 60 * 60), get_line_no()])

    def export(self):
        def ppe(e):
            if hasattr(e, "export"):
                return e.export()
            if isinstance(e, str):
                return '"%s"' % e
            return str(e)
        if self._f == "invalid":
            raise Exception(" ".join(str(x) for x in self._l))
        if self._l:
            return "(%s %s)" % (self._f, " ".join(ppe(x) for x in self._l))
        return "(%s)" % (self._f)


def literal(t, l):
    return Expr("literal", [Expr(t, [l]), get_line_no()])


def key_hash(s):
    return literal("key_hash", s)


def variant(cons, x):
    return Expr("variant", [cons, spExpr(x), get_line_no()])


unit = Expr("unit", [])


def bool(x):
    return literal("bool", x)


def int(x):
    return literal("int", x)


def int_or_nat(x):
    return literal("intOrNat", x)


def nat(x):
    return literal("nat", x)


def string(x):
    return literal("string", x)


_hex_digits = set("0123456789abcdefABCDEF")


def bytes(x):
    if (
        isinstance(x, str)
        and x.startswith("0x")
        and all(c in _hex_digits for c in x[2:])
        and pyLen(x) % 2 == 0
    ):
        return literal("bytes", x)
    raise Exception(
        "sp.bytes('0x...') awaits a string in hexadecimal format and got '%s' line %i."
        % (str(x), get_line_no())
    )


def chain_id_cst(x):
    if (
        isinstance(x, str)
        and x.startswith("0x")
        and all(c in _hex_digits for c in x[2:])
        and pyLen(x) % 2 == 0
    ):
        return literal("chain_id_cst", x)
    raise Exception(
        "sp.chain_id_cst('0x...') awaits a string in hexadecimal format and got '%s' line %i."
        % (str(x), get_line_no())
    )


chain_id = Expr("chain_id", [])
none = Expr("variant", ["None", unit, -1])

def some(x):
    return Expr("variant", ["Some", spExpr(x), get_line_no()])


def left(x):
    return Expr("variant", ["Left", spExpr(x), get_line_no()])


def right(x):
    return Expr("variant", ["Right", spExpr(x), get_line_no()])


def mutez(x):
    return literal("mutez", x) if isinstance(x, pyInt) else split_tokens(mutez(1), x, 1)


def timestamp(seconds):
    return literal("timestamp", seconds)


def timestamp_from_utc(year, month, day, hours, minutes, seconds):
    return timestamp(
        pyInt(
            datetime.datetime(
                year, month, day, hours, minutes, seconds, tzinfo=datetime.timezone.utc
            ).timestamp()
        )
    )


def timestamp_from_utc_now():
    return timestamp(pyInt(datetime.datetime.now(datetime.timezone.utc).timestamp()))


def address(s):
    if s == "":
        raise Exception('"" is not a valid address')
    if not (any(s.startswith(prefix) for prefix in ["KT1", "tz1", "tz2", "tz3"])):
        raise Exception(
            '"%s" is not a valid address, it should start with tz1, tz2, tz3 or KT1.'
            % s
        )
    return literal("address", s)


def key(s):
    return literal("key", s)


def secret_key(s):
    return literal("secret_key", s)


def signature(sig):
    return literal("signature", sig)


def hash_key(x):
    return Expr("hash_key", [spExpr(x), get_line_no()])


def tez(x):
    return (
        literal("mutez", 1000000 * x)
        if isinstance(x, pyInt)
        else split_tokens(tez(1), x, 1)
    )


def spExpr(x, context = "expression"):
    debug = False  # isinstance(x, dict)
    if x is None:
        raise Exception("Unexpected value (None) for %s in line %i." % (context, get_line_no()))
    if isinstance(x, Local):
        raise Exception(
            "Local value of variable %s can be accessed by doing %s.value"
            % (x.name, x.name)
        )
    if isinstance(x, Expr):
        if debug:
            alert("Expr")
        return x
    if x == ():
        if debug:
            alert("unit")
        return unit
    if isinstance(x, float):
        if debug:
            alert("float")
        return literal("float", x)
    if isinstance(x, pyBool):
        if debug:
            alert("bool")
        return literal("bool", x)
    if isinstance(x, pyInt):
        if debug:
            alert("int")
        if x < 0:
            return literal("int", x)
        return literal("intOrNat", x)
    if hasattr(x, "__int__"):
        return literal("intOrNat", pyInt(x))
    if isinstance(x, str):
        if debug:
            alert("str")
        return literal("string", x)
    if isinstance(x, pyBytes):
        if debug:
            alert("bytes")
        return literal("bytes", x.decode())
    if isinstance(x, WouldBeValue):
        if debug:
            alert("WouldBeValue")
        return x
    if isinstance(x, dict):
        if debug:
            alert("dict")
        return map(x)
    if isinstance(x, pySet):
        if any(isinstance(y, Expr) for y in x):
            raise Exception(
                "{e1, ..., en} syntax is forbidden for SmartPy Expr. Please use sp.set([e1, .., en])"
            )
        return set([spExpr(y) for y in x])
    if isinstance(x, pyTuple):
        if debug:
            alert("tuple")
        return tuple([spExpr(y) for y in x])
    if isinstance(x, pyList):
        if debug:
            alert("list")
        return list([spExpr(y) for y in x])
    if isinstance(x, pyRange):
        if debug:
            alert(x)
            alert("range")
        return list(pyList(x))
    if isinstance(x, Lambda):
        if debug:
            alert(x)
            alert("Lambda")
        return x.f
    if isinstance(x, GlobalLambda):
        if debug:
            alert(x)
            alert("Lambda")
        return Expr("global", [x.name, get_line_no()])
    if isinstance(x, FunctionType):
        if debug:
            alert(x)
            alert("FunctionType")
        return build_lambda(x).f
    if isinstance(x, TestAccount):
        if debug:
            alert(x)
            alert("TestAccount")
        return x.e
    if isinstance(x, TType):
        if debug:
            alert(x)
            alert("TType")
        raise Exception("spExpr: using type expression %s as an expression" % (str(x)))
    if isinstance(x, Verbatim):
        return x
    raise Exception("spExpr: '%s' of type '%s'" % (str(x), str(type(x))))


class TType:
    def __repr__(self):
        return self.export()


class TRecord(TType):
    def __init__(self, **kargs):
        args = {}
        for (k, v) in kargs.items():
            v = sp.types.conv(v)
            args[k] = v
            setattr(self, k, v)
        self.kargs = args
        self.layout_ = None

    def layout(self, layout):
        result = TRecord(**dict(self.kargs))
        result.layout_ = parse_layout(layout)
        return result

    def right_comb(self):
        result = TRecord(**dict(self.kargs))
        result.layout_ = "Right"
        return result

    def with_fields(self, **kargs):
        result = dict(self.kargs)
        for (k, v) in kargs.items():
            result[k] = v
        return TRecord(**result)

    def without_fields(self, l):
        result = dict(self.kargs)
        for k in l:
            del result[k]
        return TRecord(**result)

    def export(self):
        fields = " ".join(
            "(%s %s)" % (x, y.export()) for (x, y) in sorted(self.kargs.items())
        )
        layout = ("(Some %s)" % self.layout_) if self.layout_ else "None"
        return "(record (%s) %s)" % (fields, layout)

def parse_layout(layout):
    if isinstance(layout, pyTuple):
        if pyLen(layout) != 2:
            raise Exception("Layout computation on non-pair %s" % (str(layout)))
        return '(%s %s)' % (parse_layout(layout[0]), parse_layout(layout[1]))
    if isinstance(layout, str):
        return '("%s")' % layout
    raise Exception("Layout computation on non-pair or str %s" % (str(layout)))


class ExprStr:
    def __init__(self, s):
        self.s = s

    def export(self):
        return self.s


def set_record_layout(expression, layout):
    result = Expr("set_record_layout", [spExpr(expression), ExprStr(parse_layout(layout)), get_line_no()])
    sp.newCommand(result)
    return result


def set_variant_layout(expression, layout):
    result = Expr("set_variant_layout", [spExpr(expression), ExprStr(parse_layout(layout)), get_line_no()])
    sp.newCommand(result)
    return result


def set_type_record_layout(expression, layout):
    result = Expr("set_type_record_layout", [sp.types.conv(expression), ExprStr(parse_layout(layout)), get_line_no()])
    sp.newCommand(result)
    return result


def set_type_variant_layout(expression, layout):
    result = Expr("set_type_variant_layout", [sp.types.conv(expression), ExprStr(parse_layout(layout)), get_line_no()])
    sp.newCommand(result)
    return result


class TVariant(TType):
    def __init__(self, **kargs):
        args = sorted(kargs.items())
        self.kargs = kargs
        self.layout_ = None
        for (k, v) in args:
            setattr(self, k, sp.types.conv(v))

    def layout(self, layout):
        self.layout_ = parse_layout(layout)
        return self

    def right_comb(self):
        self.layout_ = "Right"
        return self

    def export(self):
        fields = " ".join(
            "(%s %s)" % (x, y.export()) for (x, y) in sorted(self.kargs.items())
        )
        layout = ("(Some %s)" % self.layout_) if self.layout_ else "None"
        return "(variant (%s) %s)" % (fields, layout)


def TOr(tleft, tright):
    return TVariant(Left=tleft, Right=tright)


class TSimple(TType):
    def __init__(self, name):
        self.name = name

    def export(self):
        return '"%s"' % self.name


TUnit = TSimple("unit")
TBool = TSimple("bool")
TInt = TSimple("int")
TNat = TSimple("nat")
TIntOrNat = TSimple("intOrNat")
TString = TSimple("string")
TBytes = TSimple("bytes")
TMutez = TSimple("mutez")
TTimestamp = TSimple("timestamp")
TAddress = TSimple("address")
TKey = TSimple("key")
TSecretKey = TSimple("secret_key")
TKeyHash = TSimple("key_hash")
TSignature = TSimple("signature")
TChainId = TSimple("chain_id")
TOperation = TSimple("operation")
TSaplingState = TSimple("sapling_state")
TSaplingTransaction = TSimple("sapling_transaction")
TNever = TSimple("never")


class TUnknown(TType):
    def __init__(self, id):
        self.id = id

    def export(self):
        return '(unknown %i)' % self.id


class TList(TType):
    def __init__(self, t):
        self.t = sp.types.conv(t)

    def export(self):
        return "(list %s)" % self.t.export()


class TMap(TType):
    def __init__(self, k, v):
        self.k = sp.types.conv(k)
        self.v = sp.types.conv(v)

    def export(self):
        return "(map %s %s)" % (self.k.export(), self.v.export())


class TSet(TType):
    def __init__(self, t):
        self.t = sp.types.conv(t)

    def export(self):
        return "(set %s)" % self.t.export()


class TBigMap(TType):
    def __init__(self, k, v):
        self.k = sp.types.conv(k)
        self.v = sp.types.conv(v)

    def export(self):
        return "(bigmap %s %s)" % (self.k.export(), self.v.export())


class TPair(TType):
    def __init__(self, t1, t2):
        self.t1 = t1
        self.t2 = t2

    def export(self):
        return "(pair %s %s)" % (
            sp.types.conv(self.t1).export(),
            sp.types.conv(self.t2).export(),
        )


class TAnnots(TType):
    def __init__(self, t, *annots):
        self.t = sp.types.conv(t)
        self.annots = annots

    def export(self):
        return "(annots %s (%s))" % (
            self.t.export(),
            " ".join('"%s"' % a for a in self.annots),
        )


class TOption(TType):
    def __init__(self, t):
        self.t = sp.types.conv(t)

    def export(self):
        return "(option %s)" % self.t.export()


class TContract(TType):
    def __init__(self, t):
        self.t = sp.types.conv(t)

    def export(self):
        return "(contract %s)" % self.t.export()


class TLambda(TType):
    def __init__(self, t1, t2):
        self.t1 = sp.types.conv(t1)
        self.t2 = sp.types.conv(t2)

    def export(self):
        return "(lambda %s %s)" % (self.t1.export(), self.t2.export())


class SpTypes:
    def __init__(self):
        self.unknownIds = 0
        self.seqCounter = 0

    def conv(self, t):
        if isinstance(t, WouldBeValue):
            raise Exception("Bad type expression " + str(t))
        if t is None:
            t = self.unknown()
        # This line needs to come before lines with ==.
        if isinstance(t, TType) or isinstance(t, Expr):
            return t
        if t == pyInt:
            raise Exception("Type int in this context is referred to as sp.TInt.")
        if t == pyBool:
            raise Exception("Type bool in this context is referred to as sp.TBool.")
        if t == str:
            raise Exception("Type str in this context is referred to as sp.TString.")
        if t == pyBytes:
            raise Exception("Type bytes in this context is referred to as sp.TBytes.")
        if isinstance(t, pyList) and pyLen(t) == 1:
            return TList(self.conv(t[0]))
        raise Exception("Bad type expression " + str(t) + " of type " + str(type(t)))

    def trecord(self, **kargs):
        for x in kargs:
            kargs[x] = self.conv(kargs[x])
        return TRecord(kargs)

    def unknown(self):
        self.unknownIds += 1
        return TUnknown(self.unknownIds)

    def seqNo(self):
        self.seqCounter += 1
        return self.seqCounter

    def taddress(self):
        return TAddress

    def tlist(self, t):
        return TList(t)


class Data:
    def __getattr__(self, attr):
        if "__" in attr:
            raise AttributeError("")
        return Expr("attr", [Expr("data", []), attr])

    def __setattr__(self, attr, value):
        sp.set(getattr(self, attr), value)


class TreeBlock:
    def __init__(self):
        self.commands = []
        self.locals = []

    def append(self, command):
        self.commands.append(command)

    def addLocal(self, var):
        self.locals.append(var)

    def export(self):
        return "(%s)" % (" ".join(x.export() for x in self.commands))


class CommandBlock:
    def __init__(self, sp):
        self.sp = sp
        self.commands = TreeBlock()
        self.value = None

    def __enter__(self):
        self.currentBlock = self.sp.mb.currentBlock
        self.sp.mb.currentBlock = self.commands
        return self.value

    def __exit__(self, type, value, traceback):
        self.sp.mb.currentBlock = self.currentBlock

    def export(self):
        return self.commands.export()


class Sp:
    def __init__(self):
        self.types = SpTypes()
        self.profiling = False
        self.profilingLogs = []
        self.mb = None

    def profile(self, s=""):
        if self.profiling:
            import datetime

            self.profilingLogs.append(str(datetime.datetime.now()) + " " + s)

    def setMB(self, mb):
        self.mb = mb

    def delItem(self, expr, item):
        self.newCommand(Expr("delItem", [expr, spExpr(item), get_line_no()]))

    def cons(self, x, xs):
        return Expr("cons", [spExpr(x), spExpr(xs), get_line_no()])

    def newCommand(self, command):
        if hasattr(self, "mb") and self.mb is not None:
            self.mb.append(command)
        else:
            raise Exception("New command outside of contract (line %i):\n%s" % (get_line_no(), str(command)))

    def set(self, var, value):
        if value is None:
            raise Exception("None value for ", var)
        self.newCommand(Expr("set", [var, spExpr(value), get_line_no()]))

    def updateSet(self, set, item, add):
        self.newCommand(
            Expr("updateSet", [spExpr(set), spExpr(item), add, get_line_no()])
        )

    def defineLocal(self, local, name, value):
        self.newCommand(Expr("defineLocal", [name, value, get_line_no()]))
        self.mb.addLocal(local)

    def getData(self):
        return Expr("data", [])


sp = Sp()


class MessageBuilder:
    def __init__(self, addedMessage):
        if addedMessage is not None:
            self.name = addedMessage.name
            self.addedMessage = addedMessage
        self.commands = TreeBlock()
        self.currentBlock = self.commands

    def append(self, command):
        self.currentBlock.append(command)

    def addLocal(self, var):
        self.currentBlock.addLocal(var)

    def export(self):
        return self.commands.export()

    def __repr__(self):
        return "Commands:%s" % (" ".join(str(command) for command in self.commands))

    def pp(self):
        output = ["    " + (command.pp()) for command in self.commands]
        return "\n".join(outputs)


class ExecutedMessage:
    def __init__(self, title, result, expected):
        self.title = title
        self.result = result
        self.expected = expected

    def html(self):
        return (
            ""
            if self.expected
            else "<br><span class='partialType'>ERROR: Unexpected result</span> please use .run(valid = ..expected validation..)<br>"
        ) + self.result

    def __repr__(self):
        return self.html()


class PreparedMessage:
    def __init__(self):
        pass

    def html(self):
        data = {}
        data["action"] = "message"
        data["id"] = self.contractId
        data["message"] = self.message
        data["params"] = self.params
        data["line_no"] = self.lineNo
        data["title"] = self.title
        data["messageClass"] = self.messageClass
        data["source"] = self.source
        data["sender"] = self.sender
        data["chain_id"] = self.chain_id
        data["time"] = self.time
        data["amount"] = self.amount
        data["level"] = self.level
        data["show"] = self.show
        data["valid"] = self.valid
        return [data]


def reduce(value):
    return Expr("reduce", [spExpr(value), get_line_no()])


class TestAccount:
    def __init__(self, seed):
        self.seed = seed
        self.e = Expr("account_of_seed", [self.seed, get_line_no()])
        self.address = reduce(self.e.address)
        self.public_key_hash = reduce(self.e.public_key_hash)
        self.public_key = reduce(self.e.public_key)
        self.secret_key = reduce(self.e.secret_key)

    def export(self):
        return self.e.export()


def test_account(seed):
    return TestAccount(seed)


# sp.sign is already taken by the sign as in plus or minus
def make_signature(secret_key, message, message_format="Raw"):
    return reduce(
        Expr(
            "make_signature",
            [spExpr(secret_key), spExpr(message), message_format, get_line_no()],
        )
    )


def parse_account_or_address(account, name):
    if account is None:
        return "none"
    if isinstance(account, TestAccount):
        return "seed:" + account.seed
    if (
        isinstance(account, Expr)
        and account._f == "literal"
        and account._l[0]._f == "address"
    ):
        return "address:" + str(account)
    raise Exception(
        "%s should be of the form sp.test_account('...') or sp.address(...) : %s"
        % (name, str(account))
    )


class ExecMessage:
    def __init__(self, _contract, _message, params, kargs):
        self.message = _message
        self.params = None if params is None else spExpr(params)
        self.kargs = (
            None if kargs is None else {k: spExpr(v) for (k, v) in kargs.items()}
        )
        if params is not None and kargs:
            raise Exception(
                "Message execution uses either one args or *kargs syntax, not both."
            )
        self.contract = _contract
        self.smartml = _contract.smartml
        self.lineNo = get_line_no()

    def html(self):
        return self.run().html()

    def run(
        self,
        sender=None,
        source=None,
        amount=mutez(0),
        now=None,
        level=None,
        valid=True,
        show=True,
        chain_id=None,
    ):
        sp.profile(self.message + " begin " + str(get_line_no()))
        if isinstance(now, Expr) and now._f == "literal":
            now = now._l[0]
        if isinstance(amount, pyInt):
            raise Exception(
                "Amount should be in tez or mutez and not int (use sp.tez(..) or sp.mutez(..))"
            )
        if isinstance(now, Expr) and now._f == "timestamp":
            now = now._l[0]
        if now is not None:
            if not isinstance(now, pyInt):
                raise Exception("bad now " + str(now))
            self.smartml.setNow(now)
        if level is not None:
            if not isinstance(level, pyInt):
                raise Exception("bad level " + str(level))
            self.smartml.setLevel(level)
        if self.params is None:
            self.params = record(**self.kargs)
        if chain_id is None:
            chain_id = ""
        else:
            chain_id = chain_id.export()
        self.contract.data = Expr(
            "contractData", [self.smartml.contractId, get_line_no()]
        )
        result = PreparedMessage()
        result.lineNo = self.lineNo
        result.title = self.contract.title if self.contract.title else ""
        result.messageClass = self.contract.execMessageClass
        result.source = parse_account_or_address(source, "Source")
        result.sender = parse_account_or_address(sender, "Sender")
        result.chain_id = chain_id
        result.time = self.smartml.time
        result.amount = amount.export()
        result.level = self.smartml.level
        result.contractId = self.smartml.contractId
        result.message = self.message
        result.params = self.params.export()
        result.valid = valid
        result.show = show
        sp.profile(self.message + " end")
        return result


class WouldBeValue:
    def __repr__(self):
        try:
            return self.export()
        except:
            return "value of type %s at line %i" % (
                self.__class__.__name__,
                get_line_no(),
            )


class record(WouldBeValue):
    def __init__(self, **fields):
        self.fields = {k: spExpr(v) for (k, v) in fields.items()}
        for (k, v) in self.fields.items():
            setattr(self, k, v)
        self.lineNo = get_line_no()

    def export(self):
        return "(record %i %s)" % (
            self.lineNo,
            " ".join(
                "(%s %s)" % (k, v.export()) for (k, v) in sorted(self.fields.items())
            ),
        )


class tuple(WouldBeValue):
    def __init__(self, l = None):
        if l is None:
            l = []
        self.l = l
        self.lineNo = get_line_no()

    def export(self):
        return "(tuple %s %s)" % (
            " ".join(spExpr(x).export() for x in self.l),
            self.lineNo,
        )


def pair(e1, e2):
    return tuple([e1, e2])


class build_list(WouldBeValue):
    def __init__(self, l = None):
        if l is None:
            l = []
        self.l = l
        self.lineNo = get_line_no()

    def push(self, other):
        return sp.set(self, sp.cons(spExpr(other), self))

    def map(self, f):
        return Expr("map_function", [self, spExpr(f), get_line_no()])

    def export(self):
        return "(list %s %s)" % (
            self.lineNo,
            " ".join(spExpr(x).export() for x in self.l),
        )

    def concat(self):
        return Expr("concat", [self, get_line_no()])

    def rev(self):
        return Expr("rev", [self, get_line_no()])


class build_set(WouldBeValue):
    def __init__(self, l = None):
        if l is None:
            l = []
        self.l = l
        self.lineNo = get_line_no()

    def contains(self, value):
        return Expr("contains", [self, spExpr(value), get_line_no()])

    def elements(self):
        return Expr("elements", [self, get_line_no()])

    def rev_elements(self):
        return Expr("rev_elements", [self, get_line_no()])

    def add(self, item):
        self.l.append(item)

    def remove(self, item):
        raise Exception(
            "set.remove not implemented for immediate value, please use a local variable."
        )

    def export(self):
        return "(set %s %s)" % (
            self.lineNo,
            " ".join(spExpr(x).export() for x in self.l),
        )


class mapOrBigMap(WouldBeValue):
    def __init__(self, l = None):
        if l is None:
            l = {}
        self.l = l
        self.lineNo = get_line_no()

    def contains(self, value):
        return Expr("contains", [self, spExpr(value), get_line_no()])

    def __getitem__(self, item):
        return Expr("getItem", [self, spExpr(item), get_line_no()])

    def export(self):
        return "(%s %s %s)" % (
            self.name(),
            self.lineNo,
            " ".join(
                "(%s %s)" % (spExpr(k).export(), spExpr(v).export())
                for (k, v) in self.l.items()
            ),
        )


class build_map(mapOrBigMap):
    def name(self):
        return "map"

    def items(self):
        return Expr("items", [self, get_line_no()])

    def keys(self):
        return Expr("keys", [self, get_line_no()])

    def values(self):
        return Expr("values", [self, get_line_no()])

    def rev_items(self):
        return Expr("rev_items", [self, get_line_no()])

    def rev_keys(self):
        return Expr("rev_keys", [self, get_line_no()])

    def rev_values(self):
        return Expr("rev_values", [self, get_line_no()])

class build_big_map(mapOrBigMap):
    def name(self):
        return "big_map"

def list(l = None, t = None):
    l = build_list(l)
    return l if t is None else set_type_expr(l,TList(t))

def set(l = None, t = None):
    l = build_set(l)
    return l if t is None else set_type_expr(l,TSet(t))

def map_or_big_map(big, l, tkey, tvalue):
    l = build_big_map(l) if big else build_map(l)
    if tkey is None and tvalue is None:
        return l
    else:
        t = TBigMap(tkey,tvalue) if big else TMap(tkey,tvalue)
        return set_type_expr(l,t)

def map(l = None, tkey = None, tvalue = None):
    return map_or_big_map(False, l, tkey, tvalue)

def big_map(l = None, tkey = None, tvalue = None):
    return map_or_big_map(True, l, tkey, tvalue)

class Smartml:
    def __init__(self, contract=None):
        self.ctx = window.smartmlCtx
        self.time = 0
        self.level = 0
        if contract is not None:
            sp.profile("smartml linking")
            sp.profile("smartml export")
            self.contractId = window.nextId()
            window.contracts[self.contractId] = self
            self.contract = contract
            sp.profile("smartml link")

    def runScenario(self, messages):
        self.ctx.call("runScenarioInBrowser", messages)

    def setNow(self, time):
        self.time = time
        return "Setting time to [%s].<br>" % time

    def setLevel(self, level):
        self.level = level
        return "Setting level to [%s].<br>" % level


class Contract:
    def __init__(self, **kargs):
        self.init_type(t = sp.types.unknown())

    def add_flag_lazy_entry_points(self):
        self.add_flag("lazy_entry_points")

    def add_flag_lazy_entry_points_multiple(self):
        self.add_flag("lazy_entry_points_multiple")

    def add_flag(self, flag):
        if not hasattr(self, "flags"):
            self.flags = pySet()
        self.flags.update([flag])

    def global_lambda(self, name, f):
        return self.global_variable(name, build_lambda(f, global_name=name))

    def global_variable(self, name, v):
        if not hasattr(self, "global_variables"):
            self.global_variables = []
        self.global_variables.append((name, spExpr(v)))
        return Expr("global", [name, get_line_no()])

    def set_storage(self, storage):
        if self.storage is None:
            self.storage = storage
        else:
            raise Exception("Storage already set on contract (line %i)" % (get_line_no()))

    def set_initial_balance(self, balance):
        if isinstance(balance, pyInt):
            raise Exception(
                "balance should be in tez or mutez and not int (use sp.tez(..) or sp.mutez(..))"
            )
        if self.__initial_balance is None:
            self.__initial_balance = balance
        else:
            raise Exception("Balance already set on contract (line %i)" % (get_line_no()))

    def init_internal(self):
        self.currentBlock = None
        if not hasattr(self, "verbose"):
            self.verbose = False
        if not hasattr(self, "messages"):
            self.messages = {}
        if not hasattr(self, "global_variables"):
            self.global_variables = []
        if not hasattr(self, "flags"):
            self.flags = pySet()
        if not hasattr(self, "execMessageClass"):
            self.execMessageClass = ""
        if not hasattr(self, "title"):
            self.title = ""
        if not hasattr(self, "messages_collected"):
            self.messages_collected = False
        if not hasattr(self, "storage"):
            self.storage = None
        if not hasattr(self, "__initial_balance"):
            self.__initial_balance = None
        if not hasattr(self, "storage_type"):
            self.storage_type = None
        if not hasattr(self, "storage_layout"):
            self.storage_layout = None
        if not hasattr(self, "entry_points_layout"):
            self.entry_points_layout = None
        if not hasattr(self, "exception_optimization_level"):
            self.exception_optimization_level = None

    def init_type(self, t):
        self.init_internal()
        self.storage_type = t
        self.collectMessages()

    def init_storage_record_layout(self, layout):
        self.init_internal()
        self.storage_layout = parse_layout(layout)

    def init_entry_points_layout(self, layout):
        self.init_internal()
        self.entry_points_layout = parse_layout(layout)

    def init(self, **kargs):
        self.init_internal()
        if "data" in kargs:
            self.storage = kargs["data"]
        else:
            self.storage = record(**kargs)
        self.collectMessages()

    def addMessage(self, addedMessage):
        sp.profile("addMessage begin " + addedMessage.name)
        addedMessage.contract = self
        mb = MessageBuilder(addedMessage)
        self.mb = mb
        sp.setMB(mb)
        args = inspect.getargs(addedMessage.f.__code__).args
        nargs = pyLen(args)
        params = Expr("params", [addedMessage.lineNo])
        if nargs == 0:
            raise Exception("Entry point '%s' is missing a self parameter (line %i)." % (addedMessage.name, addedMessage.lineNo))
        elif nargs == 1:
            x = addedMessage.f(self)
        elif nargs == 2:
            x = addedMessage.f(self, params)
        else:
            args[0] = self
            for i in pyRange(1, nargs):
                args[i] = Expr("attr", [params, args[i], get_line_no()])
            x = addedMessage.f(*args)
        if x is not None:
            raise Exception(
                "Entry point failure for %s (line %i): entry points cannot have return statements."
                % (addedMessage.name, addedMessage.lineNo)
            )
        self.mb = None
        sp.setMB(None)
        self.messages[addedMessage.name] = mb
        mb.originate = addedMessage.originate
        setattr(self, addedMessage.name, addedMessage)
        # if not isinstance(self.data, Expr) or self.data._f != "data":
        #     raise Exception(
        #         "It's forbidden to change self.data directly.\n self.data = "
        #         + str(self.data)
        #     )
        sp.profile("addMessage end " + addedMessage.name)

    def buildExtraMessages(self):
        pass

    def collectMessages(self):
        if self.messages_collected:
            return
        sp.profile("CollectMessages begin " + self.__class__.__name__)
        self.data = sp.getData()
        for f in dir(self):
            attr = getattr(self, f)
            if isinstance(attr, GlobalLambda):
                attr._l = self.global_lambda(attr.name, attr.f)
            if isinstance(attr, SubEntryPoint):
                attr._l = self.global_lambda(attr.name, lambda x: attr.fg(self,x))
                attr.contract = self
        for f in dir(self):
            attr = getattr(self, f)
            if isinstance(attr, AddedMessage):
                self.addMessage(
                    AddedMessage(attr.name, attr.f, attr.originate, attr.lineNo)
                )
        self.buildExtraMessages()
        # self.smartml = window.buildSmartlmJS(self)
        self.smartml = Smartml(self)
        sp.profile("CollectMessages smartml " + self.__class__.__name__)
        self.data = Expr("contractData", [self.smartml.contractId, get_line_no()])
        self.balance = Expr("contractBalance", [self.smartml.contractId, get_line_no()])
        sp.profile("CollectMessages end " + self.__class__.__name__)
        self.address = contract_address(self)
        self.baker = contract_baker(self)

    def export(self):
        if self.exception_optimization_level is not None:
            self.add_flag("Exception_%s" % self.exception_optimization_level)
        result = "(storage %s\nstorage_type (%s)\nmessages (%s)\nflags (%s)\nglobals (%s)\nstorage_layout %s\nentry_points_layout %s\nbalance %s)" % (
            (self.storage.export() if self.storage is not None else "()"),
            ("%s" % (self.storage_type.export()) if self.storage_type is not None else "()"),
            (
                " ".join(
                    "(%s %s %s)" % (k, str(v.originate), v.export())
                    for (k, v) in sorted(self.messages.items())
                )
            ),
            (" ".join(str(flag) for flag in sorted(self.flags))),
            (
                " ".join(
                    "(%s %s)" % (name, variable.export())
                    for (name, variable) in self.global_variables
                )
            ),
            (self.storage_layout if self.storage_layout is not None else "()"),
            (self.entry_points_layout if self.entry_points_layout is not None else "()"),
            (self.__initial_balance.export() if self.__initial_balance is not None else "()"),
        )
        if self.verbose:
            alert("Creating\n\n%s" % result)
            window.console.log(result)
        return result

    def setNow(self, time):
        return self.smartml.setNow(time)

    def __repr__(self):
        return str(self.smartml)

    def fullHtml(self, accept_unknown_types, default="SmartPy", onlyDefault=False):
        data = {}
        data["action"] = "newContract"
        data["id"] = self.smartml.contractId
        data["export"] = self.smartml.contract.export()
        data["line_no"] = get_line_no()
        data["show"] = True
        data["accept_unknown_types"] = accept_unknown_types
        return [data]

exception_optimization_levels = ["FullDebug", "DebugMessage", "VerifyOrLine", "DefaultLine", "Line", "DefaultUnit", "Unit"]

def contract_address(c):
    return literal("local-address", c.smartml.contractId)

def contract_baker(c):
    return Expr("contract_baker", [c.smartml.contractId, get_line_no()])

class AddedMessage:
    def __init__(self, name, f, originate, lineNo):
        self.name = name
        self.f = f
        self.originate = originate
        self.lineNo = lineNo

    def __call__(self, params=None, **kargs):
        return ExecMessage(self.contract, self.name, params, kargs)


def entry_point(f, name=None):
    if name is None:
        name = f.__name__
    return AddedMessage(name, f, True, get_line_no())


def private_entry_point(f, name=None):
    if name is None:
        name = f.__name__
    return AddedMessage(name, f, False, get_line_no())


class GlobalLambda:
    def __init__(self, name, f, lineNo):
        self.name = name
        self.f = f
        self.lineNo = lineNo

    def __call__(self, x):
        return self._l(x)


def global_lambda(f, name=None):
    if name is None:
        name = f.__name__
    return GlobalLambda(name, f, get_line_no())

class SubEntryPoint:
    def __init__(self, name, f, lineNo):
        self.name = name
        self.fg = f
        self.lineNo = lineNo

    def __call__(self, x):
        data = Expr("data",[])
        y = local("y%d" % sp.types.seqNo(), self._l(record(in_param=x, in_storage=data)))
        sp.set(data, y.value.storage)
        add_operations(y.value.operations)
        return y.value.result

def sub_entry_point(f, name=None):
    def f_wrapped(self,x):
        ops     = local("__operations__", [], t = TList(TOperation))
        storage = local("__storage__", x.in_storage, t = sp.types.unknown())
        y = seq()
        with y:
            f(self, x.in_param)
        with bind(y):
            result(record(result = y.value, operations = ops.value, storage = storage.value))
    if name is None:
        name = f.__name__
    return SubEntryPoint(name, f_wrapped, get_line_no())

self = Expr("self", [])
sender = Expr("sender", [])
source = Expr("source", [])
amount = Expr("amount", [])
balance = Expr("balance", [])
now = Expr("now", [])
level = Expr("level", [])


def self_entry_point(entry_point=""):
    return Expr("self_entry_point", [entry_point, get_line_no()])


def to_address(contract):
    return Expr("to_address", [spExpr(contract), get_line_no()])


def implicit_account(key_hash):
    return Expr("implicit_account", [spExpr(key_hash), get_line_no()])


default_verify_message = None
wrap_verify_messages = None

def verify(cond, message=None, ghost=False):
    if message is None:
        message = default_verify_message
    if wrap_verify_messages is not None and message is not None:
        message = wrap_verify_messages(message)
    if message is None:
        sp.newCommand(Expr("verify", [spExpr(cond), ghost, get_line_no()]))
    else:
        sp.newCommand(
            Expr("verify", [spExpr(cond), ghost, spExpr(message), get_line_no()])
        )


def verify_equal(v1, v2, ghost=False, message=None):
    verify(poly_equal_expr(v1, v2), ghost, message)


def ghostVerify(cond, message=None):
    return verify(cond, True, message)


def failwith(message):
    sp.newCommand(Expr("failwith", [spExpr(message), get_line_no()]))

def never(parameter):
    sp.newCommand(Expr("never", [spExpr(parameter), get_line_no()]))

## Control
def else_():
    b = CommandBlock(sp)
    sp.newCommand(Expr("elseBlock", [b]))
    return b


def while_(condition):
    b = CommandBlock(sp)
    sp.newCommand(Expr("whileBlock", [spExpr(condition), b, get_line_no()]))
    return b


def match_cons(expression):
    b = CommandBlock(sp)
    sp.newCommand(Expr("match_cons", [spExpr(expression), b, get_line_no()]))
    value = Expr("match_cons", [spExpr(expression), get_line_no()])
    value.__asBlock = b
    b.value = value
    return value


def if_some(condition, name):
    b = CommandBlock(sp)
    sp.newCommand(Expr("ifSomeBlock", [spExpr(condition), name, b, get_line_no()]))
    value = Expr("openVariant", [spExpr(condition), "Some", get_line_no()])
    value.__asBlock = b
    b.value = value
    return value


def if_(condition):
    b = CommandBlock(sp)
    sp.newCommand(Expr("ifBlock", [spExpr(condition), b, get_line_no()]))
    return b


def for_(name, value):
    value = spExpr(value)
    b = CommandBlock(sp)
    t = sp.types.unknown()
    sp.newCommand(Expr("forGroup", [name, value, b, get_line_no()]))
    value = Expr("iter", [name, get_line_no()])
    value.__asBlock = b
    b.value = value
    return value


def update_map(map, key, value):
    return Expr("update_map", [spExpr(map), spExpr(key), spExpr(value), get_line_no()])

def ediv(num, den):
    return Expr("ediv", [spExpr(num), spExpr(den), get_line_no()])


def pack(value):
    return Expr("pack", [spExpr(value), get_line_no()])


def unpack(value, t = None):
    return Expr("unpack", [spExpr(value), sp.types.conv(t), get_line_no()])


def blake2b(value):
    return Expr("hashCrypto", ["BLAKE2B", spExpr(value), get_line_no()])


def sha512(value):
    return Expr("hashCrypto", ["SHA512", spExpr(value), get_line_no()])


def sha256(value):
    return Expr("hashCrypto", ["SHA256", spExpr(value), get_line_no()])


def range(a, b, step=1):
    return Expr("range", [spExpr(a), spExpr(b), spExpr(step), get_line_no()])


def sum(value):
    return Expr("sum", [value, get_line_no()])


def slice(expression, offset, length):
    return Expr(
        "slice", [spExpr(offset), spExpr(length), spExpr(expression), get_line_no()]
    )


def concat(value):
    return Expr("concat", [spExpr(value), get_line_no()])


def check_signature(pk, sig, msg):
    return Expr("check_signature", [pk, sig, msg, get_line_no()])


def sign(e):
    return Expr("sign", [e, get_line_no()])


def spmax(x, y):
    return Expr("max", [spExpr(x), spExpr(y), get_line_no()])


def spmin(x, y):
    return Expr("min", [spExpr(x), spExpr(y), get_line_no()])


def split_tokens(amount, quantity, totalQuantity):
    return Expr(
        "split_tokens",
        [spExpr(amount), spExpr(quantity), spExpr(totalQuantity), get_line_no()],
    )


def expr(v):
    return spExpr(v)


def setInt(v):
    return Expr("int", [spExpr(v), get_line_no()])


def to_int(v):
    return Expr("toInt", [spExpr(v), get_line_no()])


def is_nat(v):
    return Expr("isNat", [spExpr(v), get_line_no()])

def as_nat(v):
    return is_nat(v).open_some()

def cmd_result(r):
    return Expr("result", [spExpr(r), get_line_no()])

def result(r):
    sp.newCommand(cmd_result(r))

class Lambda:
    def __init__(self, f, params, tParams, global_name, auto_result):
        self.id = window.lambdaNextId
        self.params = params
        self.tParams = tParams
        self.global_name = global_name
        self.auto_result = auto_result
        window.lambdaNextId += 1
        self.f = self.collectLambda(f)

    def collectLambda(self, f):
        prev = sp.mb
        newMB = sp.mb is None
        if newMB:
            sp.setMB(MessageBuilder(None))
        currentBlock = sp.mb.currentBlock
        commands = TreeBlock()
        sp.mb.currentBlock = commands
        r = f(
            Expr("lambdaParams", [self.id, self.params, get_line_no(), self.tParams])
        )
        if self.auto_result:
            if r is not None:
                result(r)
        elif r is not None:
            raise Exception("Please use 'sp.result' instead of 'return' in SmartPy functions.")
        r = Expr("lambda", [self.id, self.params, get_line_no(), commands])
        sp.mb.currentBlock = currentBlock
        self.mb = prev
        if newMB:
            sp.setMB(None)
        return r

    def __call__(self, arg):
        return Expr("call_lambda", [self.f, spExpr(arg), get_line_no()])

    def apply(self, arg):
        return Expr("apply_lambda", [self.f, spExpr(arg), get_line_no()])

    def export(self):
        return self.f.export()


def build_lambda(f, params="", tParams = None, global_name=None):
    tParams = sp.types.conv(tParams)
    auto_result = f.__name__ == "<lambda>"
    return Lambda(f, params, tParams, global_name, auto_result)


class Local:
    def __init__(self, name, value, t = None):
        t = sp.types.conv(t)
        sp.defineLocal(self, name, spExpr(value))
        self.init = False
        self.name = name
        self.val = value
        self.t = t
        self.init = True

    def __getattr__(self, attr):
        if attr == "value":
            return Expr("getLocal", [self.name, get_line_no()])
        raise AttributeError(
            "Local variable '%s' doesn't have attribute %s. Use '%s.value' to access its value."
            % (self.name, attr, self.name)
        )

    def __eq__(self, other):
        raise AttributeError(
            "Local variable '%s' doesn't have attribute ==. Use '%s.value' to access its value."
            % (self.name, self.name)
        )

    def __setattr__(self, attr, value):
        if attr == "init":
            object.__setattr__(self, attr, value)
        elif attr == "value" and self.init:
            sp.set(self, spExpr(value))
        else:
            object.__setattr__(self, attr, value)

    def export(self):
        return self.value.export()


def local(name, value, t = None):
    return Local(name, set_type_expr(value,t) if t else value, t)

def compute(expression):
    return local("compute_%i" % (get_line_no()), expression).value

def sapling_empty_state():
    return Expr("sapling_empty_state", [get_line_no()])

def ensure_str(name, x):
    if not isinstance(x, str):
        raise Exception("%s should be a str literal" % name)

def ensure_int(name, x):
    if not isinstance(x, pyInt):
        raise Exception("%s should be an int literal" % name)

def sapling_test_transaction(source, target, amount):
    if source is None:
        source = ""
    if target is None:
        target = ""
    ensure_str("test_sapling_transaction source", source)
    ensure_str("test_sapling_transaction target", target)
    ensure_int("test_sapling_transaction amount", amount)
    if amount < 0:
        raise Exception("test_sapling_transaction amount should be non-negative")
    return Expr("sapling_test_transaction", [source, target, str(amount), get_line_no()])

def operations():
    return Expr("operations", [get_line_no()])

def add_operations(l):
    with for_('op', l) as op:
        operations().push(op)

def transfer_operation(arg, amount, destination):
    return Expr(
        "transfer",
        [spExpr(arg, "transfer arguments"), spExpr(amount, "transfer amount"), spExpr(destination, "transfer destination"), get_line_no()],
    )

def transfer(arg, amount, destination):
    operations().push(transfer_operation(arg, amount, destination))

def set_delegate_operation(key_hash):
    return Expr("set_delegate", [spExpr(key_hash), get_line_no()])

def set_delegate(key_hash):
    operations().push(set_delegate_operation(key_hash))

def contract(t, address, entry_point=""):
    t = sp.types.conv(t)
    return Expr(
        "contract", [entry_point, sp.types.conv(t), spExpr(address), get_line_no()]
    )

def create_contract(contract, storage = None, amount = tez(0), baker = None):
    line_no = get_line_no()
    x = local('create_contract_%i' % line_no, Expr("create_contract", [Expr("contract", [contract]),
                                                                       Expr("storage", [spExpr(storage) if storage is not None else storage]),
                                                                       Expr("baker", [spExpr(baker) if baker is not None else baker]),
                                                                       Expr("amount", [spExpr(amount)]),
                                                                       line_no]))
    operations().push(x.value.operation)
    return x.value.address

def set_type_expr(expression, t):
    result = Expr("type_annotation", [spExpr(expression), sp.types.conv(t), get_line_no()])
    return result


def set_type(expression, t):
    result = Expr("set_type", [spExpr(expression), sp.types.conv(t), get_line_no()])
    sp.newCommand(result)
    return Expr("invalid", ["Invalid expression, sp.set_type should no longer be used as an expression, please use sp.set_type_expr instead (line: %i)" % get_line_no()])


def profile(s):
    sp.profile(s)


def setProfiling(b):
    sp.profiling = b
    sp.profilingLogs = []


def fst(e):
    return Expr("first", [spExpr(e), get_line_no()])


def snd(e):
    return Expr("second", [spExpr(e), get_line_no()])


def len(e):
    return Expr("size", [spExpr(e), get_line_no()])


types = sp.types

import smartpyio

normalMax = max
smartpyio.mymax = spmax
max = spmax
min = spmin


def poly_equal_expr(a, b):
    t = sp.types.unknown()
    return pack(set_type_expr(a, t)) == pack(set_type_expr(b, t))


class Scenario:
    def __init__(self):
        self.messages = []
        self.smartml = Smartml(None)
        self.exceptions = []
        self.nextId = 0

    def acc(self, message, show):
        if isinstance(message, str):
            if show:
                self.messages.append(message)
        else:
            self.messages += [self.setShow(x, show) for x in message]

    def setShow(self, x, show):
        x["show"] = show
        return x

    def register(self, element, show=False, accept_unknown_types=False):
        if isinstance(element, Contract):
            self.acc(element.fullHtml(accept_unknown_types), show)
        else:
            self.acc(element.html(), show)

    def __iadd__(self, element):
        self.register(element, True)
        return self

    def add(self, *elements):
        for element in elements:
            self.register(element, True)
        return self

    def pp(self):
        if window.in_browser:
            import javascript

            sp.profile("scenario - clean ui " + self.__class__.__name__)
            window.setOutput("")
            sp.profile("scenario - prepare messages " + self.__class__.__name__)
            messages = javascript.JSON.stringify(self.messages)
            sp.profile("scenario - run " + self.__class__.__name__)
            self.smartml.runScenario(messages)
            sp.profile("scenario - done " + self.__class__.__name__)
        else:
            window.setOutput(self.messages)
        return self

    def verify(self, condition):
        if isinstance(condition, pyBool):
            if not condition:
                raise Exception("Assert Failure")
        else:
            data = {}
            data["action"] = "verify"
            data["condition"] = condition.export()
            data["line_no"] = get_line_no()
            self.messages += [data]
        return self

    def verify_equal(self, v1, v2):
        data = {}
        data["action"] = "verify"
        data["condition"] = poly_equal_expr(v1, v2).export()
        data["line_no"] = get_line_no()
        self.messages += [data]
        return self

    def compute(self, expression):
        id = self.nextId
        data = {}
        data["action"] = "compute"
        data["expression"] = spExpr(expression).export()
        data["id"] = id
        data["line_no"] = get_line_no()
        self.messages += [data]
        self.nextId += 1
        return Expr("scenario_var", [id, get_line_no()])

    def show(self, expression, html=True, stripStrings=False):
        data = {}
        data["action"] = "show"
        data["html"] = html
        data["stripStrings"] = stripStrings
        data["expression"] = spExpr(expression).export()
        data["line_no"] = get_line_no()
        self.messages += [data]
        return self

    def table_of_contents(self):
        return self.tag("p", "[[TABLEOFCONTENTS]]")

    def p(self, s):
        return self.tag("p", s)

    def h1(self, s):
        return self.tag("h1", s)

    def h2(self, s):
        return self.tag("h2", s)

    def h3(self, s):
        return self.tag("h3", s)

    def h4(self, s):
        return self.tag("h4", s)

    def tag(self, tag, s):
        data = {}
        data["action"] = "html"
        data["tag"] = tag
        data["inner"] = s
        data["line_no"] = get_line_no()
        self.messages += [data]
        return self

    def simulation(self, c):
        if window.in_browser:
            data = {}
            data["action"] = "simulation"
            data["id"] = c.smartml.contractId
            data["line_no"] = get_line_no()
            self.messages += [data]
        else:
            self.p("No interactive simulation available outofbrowser.")


def test_scenario():
    scenario = Scenario()
    window.activeScenario = scenario
    return scenario

def send(destination, amount):
    transfer(unit, amount, contract(TUnit, destination).open_some())


# For backward "compatibility"
def Record(**args):
    raise Exception("sp.Record is obsolete, please use sp.record.")


def BigMap(**args):
    raise Exception("sp.BigMap is obsolete, please use sp.big_map.")


def Map(**args):
    raise Exception("sp.Map is obsolete, please use sp.map.")


def Set(**args):
    raise Exception("sp.Set is obsolete, please use sp.set.")


# Library

def vector_raw(xs):
    return map(l={k: v for (k, v) in enumerate(xs)})

def matrix_raw(xs):
    return vector_raw([vector_raw(x) for x in xs])

def cube_raw(xs):
    return vector_raw([matrix_raw(x) for x in xs])

def vector(xs, tkey = TIntOrNat, tvalue = None):
    return set_type_expr(vector_raw(xs), TMap(tkey, tvalue))

def matrix(xs, tkey = TIntOrNat, tvalue = None):
    return set_type_expr(matrix_raw(xs), TMap(tkey, TMap(tkey, tvalue)))

def cube(xs, tkey = TIntOrNat, tvalue = None):
    return set_type_expr(cube_raw(xs), TMap(tkey, TMap(tkey, TMap(tkey, tvalue))))

in_browser = window.in_browser


def add_test(*args, **kargs):
    return smartpyio.add_test(*args, **kargs)

def show(contract, name="Simulation", shortname=None, profile=False, is_default=True):
    def test():
        scenario = test_scenario()
        scenario += contract
        scenario.simulation(contract)
    return smartpyio.add_test(name = name, shortname = shortname, profile = profile, is_default = is_default)(test)

def import_template(name):
    if in_browser:
        directory = "."
    else:
        import pathlib
        directory = pathlib.Path(__file__).parent.absolute()
    template = open(str(directory) + "/templates/" + name, "r").read()
    import smartpyio
    template = smartpyio.adaptBlocks(template)
    class Mod: pass
    module = Mod()
    module.__dict__['__name__'] = "templates/" + name
    exec (template, module.__dict__)
    return module

def import_script_from_url(url):
    import urllib
    template = urllib.request.urlopen(url).read().decode('utf-8')
    import smartpyio
    template = smartpyio.adaptBlocks(template)
    class Mod: pass
    module = Mod()
    module.__dict__['__name__'] = url
    exec (template, module.__dict__)
    return module

def compile_contract(
        contract,
        target_directory,
        name = "contract"
):
    """Exports contract to smlse, code and storage files."""
    import subprocess
    import os
    os.makedirs(target_directory, exist_ok=True)
    targetSmlse = target_directory + "/" + name + ".smlse"
    open(targetSmlse, "w").write(contract.export())
    command = [
        "node",
        os.path.dirname(os.path.realpath(__file__)) + "/smartml-cli.js",
        "compile-smartml-contract",
        targetSmlse,
        target_directory
    ]
    subprocess.run(command)

class Verbatim:
    def __init__(self, s):
        self.s = s
    def export(self):
        return self.s

class Lazy_strings(build_big_map):
    def __init__(self, contract, path):
        super().__init__()
        self.next_id = 0
        self.contract = contract
        self.path = path
        self.app = None
        self.d = {}
    def get(self, x):
        result(self.path(fst(x)).get(snd(x), ""))
    def __call__(self, x):
        if not(isinstance(x, str)):
            return x
        try:
            return self.d[x]
        except KeyError:
            self.l[self.next_id] = x
            if False:
                result = self.path(self.contract.data).get(self.next_id, "")
            else:
                if self.app is None:
                    self.app = self.contract.global_lambda("get_error", self.get)
                result = self.app((self.contract.data, self.next_id))
                self.d[x] = result
            self.next_id += 1
            return result
    def export(self):
        m = Verbatim(super().export())
        return set_type_expr(m, TBigMap(TNat, TString)).export()

class seq__(object):
    def __init__(self, name, b):
        self.name = name
        self.__asBlock = b

    def __enter__(self):
        return self.__asBlock.__enter__()

    def __exit__(self, type, value, traceback):
        return self.__asBlock.__exit__(type, value, traceback)

    def __getattr__(self, attr):
        if attr == "value":
            return Expr("getLocal", [self.name, get_line_no()])
        raise AttributeError(
            "seq '%s' doesn't have attribute %s. Use '%s.value' to access its result."
            % (self.name, attr, self.name)
        )

    def export(self):
        return "(%s)" % (" ".join(c.export() for c in self.commands))

class wrapper(object):
    def __init__(self,cs): self.cs = cs
    def export(self): return "(%s)" % " ".join(c.export() for c in self.cs)

def seq(name = None):
    name = "__s%d" % sp.types.seqNo() if name is None else name
    b = CommandBlock(sp)
    sp.newCommand(Expr("seq", [name, b, get_line_no()]))
    return seq__(name, b)

def bind(c1):
    name = c1.name
    b = CommandBlock(sp)
    sp.newCommand(Expr("bind", [name, b, get_line_no()]))
    return b

def add_operations(l):
    with for_('op', l) as op:
        operations().push(op)

def lambda_with_operations(f, params="", tParams = None, global_name=None):
    def f_wrapped(x):
        ops = local("__operations__", [], t = TList(TOperation))
        y = seq()
        with y:
            f(x)
        with bind(y):
            result(pair(ops.value, y.value))
    return build_lambda(f_wrapped, params, tParams, global_name)

def lambda_operations_only(f, params="", tParams = None, global_name=None):
    def f_wrapped(x):
        ops = local("__operations__", [], t = TList(TOperation))
        f(x)
        result(ops.value)
    return build_lambda(f_wrapped, params, tParams, global_name)

def eiff(c, a, b):
    return Expr("eif", [spExpr(c), spExpr(a), spExpr(b), get_line_no()])

def eif(c, a, b):
    return eiff(c, lambda _: spExpr(a), lambda _: spExpr(b))

class Clause:
    def __init__(self, constructor, rhs):
        self.constructor = constructor
        self.rhs = rhs

    def export(self):
        return "(%s %s)" % (self.constructor, self.rhs.export())

def ematch(scrutinee, clauses):
    def f(x):
        if not (isinstance(x, pyTuple) and pyLen(x) == 2 and isinstance(x[0], str)):
            raise Exception("sp.ematch: clause is not a tuple of string and lambda")
        constructor = x[0]
        rhs = spExpr(x[1])
        return Clause(constructor, rhs)
    clauses = pyList(pyMap(f, clauses))
    return Expr("ematch", [ get_line_no(), scrutinee ] + clauses)

def eif_somef(c, a, b):
    return ematch(c, [ ("Some", a), ("None", b) ])

def eif_some(c, a, b):
    return eif_somef(c, a, lambda _: b)

def view(t):
    def app(f):
        def ep(self, params):
            view_result = seq()
            with view_result:
                f(self, fst(params))
            with bind(view_result):
                transfer(view_result.value, tez(0), contract(t, snd(params)).open_some())
        return entry_point(ep, name = f.__name__)
    return app
