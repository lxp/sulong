import mx
import os

import mx_sulong
from mx_sulong import testSuites

class ProgrammingLanguage(object):
    class PL(object):
        def __init__(self, name, exts):
            self.name = name
            self.exts = exts

    exts = {}

    @staticmethod
    def register(name, *exts):
        lang = ProgrammingLanguage.PL(name, exts)
        setattr(ProgrammingLanguage, name, lang)
        for ext in exts:
            ProgrammingLanguage.exts[ext] = lang

    @staticmethod
    def lookup(extension):
        return ProgrammingLanguage.exts.get(extension, None)

ProgrammingLanguage.register('FORTRAN', 'f90', 'f', 'f03')
ProgrammingLanguage.register('C', 'c')
ProgrammingLanguage.register('C_PLUS_PLUS', 'cpp', 'cc', 'C')
ProgrammingLanguage.register('OBJECTIVE_C', 'm')
ProgrammingLanguage.register('LLVMIR', 'll')
ProgrammingLanguage.register('LLVMBC', 'bc')
ProgrammingLanguage.register('LLVMSU', 'su')


class Optimization(object):
    class Opt(object):
        def __init__(self, name, flags):
            self.name = name
            self.flags = flags

    @staticmethod
    def register(name, *flags):
        setattr(Optimization, name, Optimization.Opt(name, list(flags)))

Optimization.register('NONE')
Optimization.register('O1', '-O1')
Optimization.register('O2', '-O2')
Optimization.register('O3', '-O3')


class Compiler(object):
    def supports(self, language):
        return language in self.supportedLanguages

class ClangCompiler(Compiler):
    def __init__(self):
        self.name = 'clang'
        self.supportedLanguages = [ProgrammingLanguage.C, ProgrammingLanguage.C_PLUS_PLUS, ProgrammingLanguage.OBJECTIVE_C]

    def compile(self, inputFile, outputFile, flags):
        return mx.run([mx_sulong.findLLVMProgram('clang'), '-S', '-emit-llvm', '-o', outputFile] + flags + [inputFile])

class GCCCompiler(Compiler):
    def __init__(self):
        self.name = 'gcc'
        self.supportedLanguages = [ProgrammingLanguage.C, ProgrammingLanguage.C_PLUS_PLUS]

    def compile(self, inputFile, outputFile, flags):
        ensureLLVMBinariesExist()
        gccPath = _toolDir + 'tools/llvm/bin/gcc'
        return mx.run([gccPath] + args)

Compiler.CLANG = ClangCompiler()
Compiler.GCC   = GCCCompiler()


class Runtime(object):
    def supports(self, language):
        return language in self.supportedLanguages

class SulongRuntime(Runtime):
    def __init__(self):
        self.name = 'sulong'
        self.supportedLanguages = [ProgrammingLanguage.LLVMIR, ProgrammingLanguage.LLVMBC, ProgrammingLanguage.LLVMSU]

    def run(self, f, args, vmArgs=None, out=None):
        if vmArgs is None:
            vmArgs = []
        return mx_sulong.runLLVM(vmArgs + [f] + args, nonZeroIsFatal=False, out=out)

class LLIRuntime(Runtime):
    def __init__(self):
        self.name = 'lli'
        self.supportedLanguages = [ProgrammingLanguage.LLVMIR, ProgrammingLanguage.LLVMBC]

    def run(self, f, args, vmArgs=None, out=None):
        return mx.run([mx_sulong.findLLVMProgram('lli'), f] + args, nonZeroIsFatal=False)

Runtime.SULONG = SulongRuntime()
Runtime.LLI    = LLIRuntime()


def getFileExtension(f):
    _, ext = os.path.splitext(f)
    return ext[1:]

def getOutputName(inputFile, compiler, optimization, target):
    base, _ = os.path.splitext(inputFile)
    outputPath = os.path.join('tests/cache', os.path.relpath(base))
    outputDir = os.path.dirname(outputPath)
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    return '%s_%s_%s.%s' % (outputPath, compiler.name, optimization.name, target.exts[0])

def multicompileFile(inputFile, compilers, flags, optimizations, target):
    base, ext = os.path.splitext(inputFile)
    lang = ProgrammingLanguage.lookup(getFileExtension(inputFile))
    for compiler in compilers:
        if compiler.supports(lang):
            for optimization in optimizations:
                outputFile = getOutputName(inputFile, compiler, optimization, target)
                if not os.path.exists(outputFile) or os.path.getmtime(inputFile) >= os.path.getmtime(outputFile):
                    #print 'Compiling %s to %s' % (inputFile, outputFile)
                    compiler.compile(inputFile, outputFile, flags + optimization.flags)
                yield outputFile

def multicompileFiles(inputFiles, compilers, flags, optimizations, target):
    for inputFile in inputFiles:
        yield inputFile, list(multicompileFile(inputFile, compilers, flags, optimizations, target))

def multicompileRecursively(path, compilers, flags, optimizations, target):
    for root, dirs, files in os.walk(path):
        for f in files:
            _, ext = os.path.splitext(f)
            if ProgrammingLanguage.lookup(ext[1:]) is not None:
                yield f, list(multicompileFile(os.path.join(root, f), compilers, flags, optimizations, target))
