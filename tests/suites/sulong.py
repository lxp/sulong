from __future__ import print_function
import sys

from tools import *

class SulongHarness(object):
    def run(self, args=None):
        testCases = []
        print('Compiling', end='')
        for inputFile, outputFiles in multicompileRecursively('projects/com.oracle.truffle.llvm.test/tests', [Compiler.CLANG], [], [Optimization.NONE], ProgrammingLanguage.LLVMIR):
            print('.', end='')
            if len(outputFiles) > 0:
                testCases.append(SulongTestCase(inputFile, outputFiles))

        print('Running', end='')
        for testCase in testCases:
            testCase.run()
            print('.', end='')

testSuites['sulong'] = SulongHarness()

class SulongTestCase(object):
    def __init__(self, inputFile, outputFiles):
        self.inputFile = inputFile
        self.outputFiles = outputFiles

    def run(self):
        results = {}
        for outputFile in self.outputFiles:
            for runtime in [Runtime.LLI, Runtime.SULONG]:
                results[(outputFile, runtime)] = runtime.run(outputFile, [])

        expectedResult = results.itervalues().next()
        for (outputFile, runtime), r in results.iteritems():
            if r != expectedResult:
                print('Expected return code %d, got %d while executing %s with %s.' % (r, expectedResult, outputFile, runtime.name))
                raise Exception('Expected return code %d, got %d while executing %s with %s.' % (r, expectedResult, outputFile, runtime.name))
