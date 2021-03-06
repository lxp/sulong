/*
 * Copyright (c) 2016, Oracle and/or its affiliates.
 *
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification, are
 * permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this list of
 * conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice, this list of
 * conditions and the following disclaimer in the documentation and/or other materials provided
 * with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its contributors may be used to
 * endorse or promote products derived from this software without specific prior written
 * permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
 * OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */
package com.oracle.truffle.llvm.tools;

import java.io.File;

import com.oracle.truffle.llvm.runtime.options.LLVMOptions;

public class LLVMToolPaths {

    static final File PROJECT_ROOT = new File(LLVMOptions.ENGINE.projectRoot() + File.separator + LLVMToolPaths.class.getPackage().getName());
    public static final File TOOLS_ROOT = new File(PROJECT_ROOT, "tools");
    public static final File LLVM_ROOT = new File(TOOLS_ROOT, "llvm/bin");

    public enum LLVMTool {
        ASSEMBLER("llvm-as"),
        COMPILER("llc"),
        CLANG("clang"),
        CLANG_PP("clang++"),
        OPT("opt");

        private final String programName;

        LLVMTool(String programName) {
            this.programName = programName;
        }
    }

    private static final File[] toolPaths = new File[LLVMTool.values().length];

    public static final File LLVM_DRAGONEGG = new File(TOOLS_ROOT, "/dragonegg/dragonegg-3.2.src/dragonegg.so");

    public static File getLLVMProgram(LLVMTool tool) {
        int toolIndex = tool.ordinal();
        if (toolPaths[toolIndex] == null) {
            toolPaths[toolIndex] = getLLVMProgram(tool.programName);
        }
        assert toolPaths[toolIndex] != null;
        return toolPaths[toolIndex];
    }

    private static File getLLVMProgram(String program) {
        return Mx.executeGetLLVMProgramPath(program);
    }

}
