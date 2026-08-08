# DeerFlow Host

The DeerFlow Host is the platform context shared by downstream products. It supplies
the runtime boundary without taking ownership of a downstream product's outcome.

## Language

**Host Runtime**:
The DeerFlow platform that provides public runtime integration to a downstream product.
_Avoid_: the research product, the research agent

**Downstream Product**:
A separately owned product that uses the Host Runtime through its public boundary.
_Avoid_: host feature, embedded DeerFlow behavior
