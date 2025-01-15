# IL2CPP-SDK-Generator
A pseudo sdk generator that distributes the structure code from the il2cpp.h file across multiple files.h depending on the dll
## Using
- Get DummyDll using Il2cppDumper
- Install [ILSpy](https://github.com/icsharpcode/ILSpy)
- Open DummyDll in ILSpy, select all the dll files and click "save code".
- Run script.py and enter the path to il2cpp.h and the folder where you saved the code.

PS: Code in the l2cpp.h file may contain errors, so the script is basically useless. :P

![Preview](https://github.com/user-attachments/assets/4fb19cba-311e-4507-b7bd-4f2119f8f046)
