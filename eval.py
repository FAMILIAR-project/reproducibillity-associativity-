import os
import subprocess

import numpy as np

GNUMBER_GENERATIONS=100
REPEAT=10
CSV_SEPARATOR=","

COLUMN_NAMES = ["Language", "Library", "System", "Compiler", "VariabilityMisc", "EqualityCheck", "NumberGenerations", "Repeat", "min", "max", "std", "mean"]

def print_column_names():
    # Print column names with separator, except for last element
    for i, col in enumerate(COLUMN_NAMES):
        if i < len(COLUMN_NAMES) - 1:
            print(col + CSV_SEPARATOR, end="")
        else:
            print(col)

def print_variant_results(variant_info, result):
    for k in result.keys():
        variant_info[k] = result[k]
    for i, col in enumerate(COLUMN_NAMES):
        if i < len(COLUMN_NAMES) - 1:
            if col in variant_info:
                print(f"{variant_info[col]}{CSV_SEPARATOR}", end="")
            elif col == "Repeat": # assuming Repeat is not the last column
                print(f"{REPEAT}{CSV_SEPARATOR}", end="")            
            else:
                print(f"{CSV_SEPARATOR}", end="")
        else:
            if col in variant_info:
                print(f"{variant_info[col]}")
            else:
                print(f"{CSV_SEPARATOR}")


def analyze_results(repeat, cmd_str):
    assert(repeat > 0)
    results = []
    for i in range(repeat):
        result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
        results.append(result.stdout.strip())
    # compute min, max, mean, std of results and store them in a dictionary
    # each element of results being a string ending with % 
    results = [float(r.replace("%", "")) for r in results]
    res = {
        "min": np.min(results),
        "max": np.max(results),
        "mean": np.mean(results), # assume repeat > 0
        "std": np.std(results),
    }
    return res


########### VARIANTS facilities to call implementations per language with some parameters


def test_PY_variants(test_name, ngen, seed=None):
    variant_info = {
    "Language": "Python",
    "Library": "std",
    "System" : "linux",
    "Compiler": "",
    "VariabilityMisc": "",
    "NumberGenerations": ngen,
    "EqualityCheck": test_name,
    }

    if seed is not None:
        variant_info["VariabilityMisc"] = f"seed {seed}"
    else:
        variant_info["VariabilityMisc"] = "no seed"

    cmd_args = ["python3", "testassoc.py", "--number", str(ngen), "--equality-check", test_name]
    if seed is not None:
        cmd_args.extend(["--seed", str(seed)])
    cmd_str = " ".join(cmd_args)
    result = analyze_results(REPEAT, cmd_str)
    print_variant_results(variant_info, result)
   

def compile_JAVA_variants():
    # execute javac -d . *.java
    cmd_args = ["javac", "-d", ".", "*.java"]
    cmd_str = " ".join(cmd_args)
    result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error while compiling Java variants")
        print(result.stderr)
        exit(1)
    

# TODO JDK version... GraalVM?
def test_JAVA_variants(rand_strategy_name, ngen, test_cmd):
    variant_info = {
        "Language": "Java",
        "Library": rand_strategy_name,
        "System": "linux",
        "Compiler": "",
        "VariabilityMisc": "",
        "NumberGenerations": GNUMBER_GENERATIONS,
        "EqualityCheck": "associativity", # TODO associativity only at the moment
    }

    cmd_args = ["java", "assoc.TestAssoc", test_cmd, str(ngen)]
    cmd_str = " ".join(cmd_args)
    result = analyze_results(REPEAT, cmd_str)
    print_variant_results(variant_info, result)

def test_C_variants(ngen):

    variant_info = {
        "Language": "C",
        "Library": "",
        "System": "",
        "Compiler": "",
        "VariabilityMisc": "",
        "NumberGenerations": ngen,
        "EqualityCheck": "associativity", # TODO associativity only supported at the moment
    }

    COMPILERS = ["gcc", "clang"]
    OPTIONS = ["-DCUSTOM=1", "", "-DWIN=1 -DCUSTOM=1", "-DWIN=1"]
    FLAGS = ["-DOLD_MAIN_C=1", ""]

    for compiler in COMPILERS:
        for i in range(4):
            for flag in FLAGS:
                cmd_args = ["./testassoc", str(ngen)]

                if compiler == "gcc" and "-DWIN=1" in OPTIONS[i]:
                    cmd_args = ["wine", "./testassoc.exe", str(ngen)]

                if compiler == "gcc" and "-DWIN=1" in OPTIONS[i]:
                    compiler = "i686-w64-mingw32-gcc"
                
                if i == 0:
                    library_name = "custom"
                    os_name = "Linux"
                elif i == 1:
                    library_name = "(srand48+drand48)"
                    os_name = "Linux"
                elif i == 2:
                    library_name = "custom"
                    if "gcc" in compiler:
                        os_name = "Windows (with wine and cross-compilation)"
                    else: # clang
                        os_name = "Linux (no cross-compilation with clang)"
                else:
                    library_name = "(srand+rand)"
                    if "gcc" in compiler:
                        os_name = "Windows (with wine and cross-compilation)"
                    else: # clang
                        os_name = "Linux (no cross-compilation with clang)"

                variant_info["Library"] = library_name
                variant_info["System"] = os_name
                variant_info["Compiler"] = compiler
                variant_info["VariabilityMisc"] = OPTIONS[i] + " " + flag
                variant_info["NumberGenerations"] = ngen
                
                # compilation
                compile_cmd_arg = [compiler, "-o", "testassoc", "testassoc.c", OPTIONS[i], flag]
                clean_compile_cmd_args = [cmd_arg for cmd_arg in compile_cmd_arg if cmd_arg != ""]

                compilation_result = subprocess.run(clean_compile_cmd_args, capture_output=True, text=True)
                if compilation_result.returncode != 0:
                    print("Error while compiling C variant")
                    print(compilation_result.stderr)
                    exit(1)         
               
                # execution 
                exec_cmd_str = " ".join(cmd_args)               
                result_str = analyze_results(REPEAT, exec_cmd_str) # TODO: wine environement debug

                print_variant_results(variant_info, result_str)


def test_RUST_variants(feature, ngen, error_margin=None):

    variant_info = {
        "Language": "Rust",
        "Library": "",
        "System": "",
        "Compiler": "",
        "VariabilityMisc": "",
        "NumberGenerations": ngen,
        "EqualityCheck": feature
    }

    if error_margin:
        variability_misc = f"--error_margin {error_margin}"
        cmd_args = ["cargo", "run", "--features", feature, "-q", "--", "--error_margin", error_margin]
    else:
        variability_misc = f"(no error margin ie pure equality)"
        cmd_args = ["cargo", "run", "--features", feature, "-q", "--"]
    
    variant_info["VariabilityMisc"] = variability_misc

    cmd_str = " ".join(cmd_args)
    result_str = analyze_results(REPEAT, cmd_str)
    print_variant_results(variant_info, result_str)


# TODO: ngen is never used since LISP is not configurable right now!
def test_LISP_variants(ngen):
    variant_info = {
        "Language": "LISP",
        "Library": "",
        "System": "",
        "Compiler": "",
        "VariabilityMisc": "",
        "NumberGenerations": ngen,
        "EqualityCheck": "associativity"
    }

    cmd_args = ["sbcl", "--noinform", "--quit", "--load", "test_assoc.lisp"]
    cmd_str = " ".join(cmd_args)
    result_str = analyze_results(REPEAT, cmd_str)
    print_variant_results(variant_info, result_str)



SEED = "42"

def test_JavaScript_variants(check, with_gseed, ngen):
    variant_info = {
        "Language": "JavaScript",
        "Library": "",
        "System": "",
        "Compiler": "",
        "VariabilityMisc": "",
        "NumberGenerations": ngen,
        "EqualityCheck": check
    }
  
    if with_gseed:
        variability_misc = "global seed"
    else:
        variability_misc = "no global seed"

    variant_info["VariabilityMisc"] = variability_misc

    npm_args = ["--prefix", "js/", "--silent", "--", "--equality-check", check, "--seed", SEED, "--number", str(ngen)]
    if with_gseed:
        npm_args.append("--with-gseed")

    npm_args_str = " ".join(npm_args)
    result_str = analyze_results(REPEAT, "npm start " + npm_args_str)
    print_variant_results(variant_info, result_str)


def test_BASH_variants(ngen, rel_eq):
    variant_info = {
        "Language": "Bash",
        "Library": "",
        "System": "",
        "Compiler": "",
        "VariabilityMisc": "",
        "NumberGenerations": ngen,
        "EqualityCheck": rel_eq
    }
      
    cmd_args = ["sh", "testassoc.sh", "-n", str(ngen), "-e", rel_eq]
    cmd_str = " ".join(cmd_args)
    result_str = analyze_results(REPEAT, cmd_str)    
    print_variant_results(variant_info, result_str)


def test_Scala_variants(ngen, rel_eq):
    variant_info = {
        "Language": "Scala",
        "Library": "",
        "System": "",
        "Compiler": "",
        "VariabilityMisc": "",
        "NumberGenerations": ngen,
        "EqualityCheck": rel_eq
    }
    # sbt is very long to start, so we use --batch to avoid the interactive mode 
    # other optimizations worth trying (but not implemented here) TODO
    # cmd_str = 'sbt -warn -Dsbt.log.noformat=true "run --seed 42 --number {} --equality-check {}"'.format(ngen, rel_eq)
    cmd_str = 'sbt --batch -warn -Dsbt.log.noformat=true "runMain Main --seed 42 --number {} --equality-check {}"'.format(ngen, rel_eq)
    result_str = analyze_results(REPEAT, cmd_str)
    print_variant_results(variant_info, result_str)


def test_Swift_variants(ngen, rel_eq):
    variant_info = {
        "Language": "Swift",
        "Library": "",
        "System": "",
        "Compiler": "",
        "VariabilityMisc": "",
        "NumberGenerations": ngen,
        "EqualityCheck": rel_eq
    }
    
    cmd_str = 'swift run --skip-build testassoc --number {} --equality-check {}'.format(ngen, rel_eq) # incredible: Swift has no --quiet mode yet https://github.com/apple/swift-package-manager/issues/4395 (dec 2022)
    result_str = analyze_results(REPEAT, cmd_str)
    print_variant_results(variant_info, result_str)


def build_Swift_variants():
    cmd_args = ["swift", "build"]
    cmd_str = " ".join(cmd_args)
    result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error while building Swift variants")
        print(result.stderr)
        exit(1)

############## Ocaml

def test_Ocaml_variants(ngen, rel_eq, seed=42):
    variant_info = {
        "Language": "Ocaml",
        "Library": "",
        "System": "",
        "Compiler": "",
        "VariabilityMisc": "",
        "NumberGenerations": ngen,
        "EqualityCheck": rel_eq
    }
    if seed is None:
        cmd_str = './testassoc --number {} --equality-check {}'.format(ngen, rel_eq)
    else:
        cmd_str = './testassoc --number {} --equality-check {} --seed {}'.format(ngen, rel_eq, seed) 
    variant_info["VariabilityMisc"] = "seed {}".format(seed)
    result_str = analyze_results(REPEAT, cmd_str)
    print_variant_results(variant_info, result_str)

def build_Ocaml_variants():
    cmd_args = ["ocamlopt", "-o", "testassoc", "testassoc.ml"]
    cmd_str = " ".join(cmd_args)
    result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error while building Ocaml variants")
        print(result.stderr)
        exit(1)


################### C++

def test_CPlusPlus_variants(ngen, rel_eq, seed=42):

    variant_info = {
            "Language": "C++",
            "Library": "",
            "System": "",
            "Compiler": "",
            "VariabilityMisc": "seed {}".format(seed),
            "NumberGenerations": ngen,
            "EqualityCheck": rel_eq, 
        }

    COMPILERS = ["g++", "clang++"]       

    for compiler in COMPILERS:       
        
        variant_info["Compiler"] = compiler
                
        # compilation
        # -fstrict-enums can be used for gcc but does not change
        # incredible discussion here: https://gcc.gnu.org/bugzilla/show_bug.cgi?id=87951
        compile_cmd_arg = [compiler, "-std=c++11", "-o", "testassoc", "testassoc.cpp"]
        
        compilation_result = subprocess.run(compile_cmd_arg, capture_output=True, text=True)
        if compilation_result.returncode != 0:
            print("Error while compiling C++ variant")
            print(compilation_result.stderr)
            exit(1)         
    
        # execution 
        if seed is None:
            cmd_args = ["./testassoc", "--number", str(ngen), "--equality-check", rel_eq]
        else:
            cmd_args = ["./testassoc", "--number", str(ngen), "--equality-check", rel_eq, "--seed", str(seed)]
        exec_cmd_str = " ".join(cmd_args)               
        result_str = analyze_results(REPEAT, exec_cmd_str) # TODO: wine environement debug

        print_variant_results(variant_info, result_str)


########### Julia

def test_Julia_variants(ngen, rel_eq, strict_equality, seed=42):
    variant_info = {
        "Language": "Julia",
        "Library": "",
        "System": "",
        "Compiler": "",
        "VariabilityMisc": "seed {}".format(seed),
        "NumberGenerations": ngen,
        "EqualityCheck": rel_eq, 
        }
    if seed is None:
        cmd_str = 'julia src/testassoc.jl --number={} --equality-check={}'.format(ngen, rel_eq)
    else:
        cmd_str = 'julia src/testassoc.jl --number={} --equality-check={} --seed={}'.format(ngen, rel_eq, seed) 
    if strict_equality:
        cmd_str += " --strict-equality=true"
        variant_info["VariabilityMisc"] += " strict-equality"
    else:
        variant_info["VariabilityMisc"] += " approximate equality of Julia lang"
    result_str = analyze_results(REPEAT, cmd_str)
    print_variant_results(variant_info, result_str)


########### R
def test_R_variants(ngen, rel_eq, seed=42):
    variant_info = {
        "Language": "R",
        "Library": "",
        "System": "",
        "Compiler": "",
        "VariabilityMisc": "seed {}".format(seed),
        "NumberGenerations": ngen,
        "EqualityCheck": rel_eq, 
        }
    if seed is None:
        cmd_str = 'Rscript testassoc.R --number={} --eq_check={}'.format(ngen, rel_eq)
    else:
        cmd_str = 'Rscript testassoc.R --number={} --eq_check={} --seed={}'.format(ngen, rel_eq, seed) 
    
    result_str = analyze_results(REPEAT, cmd_str)
    print_variant_results(variant_info, result_str)


########### Go

def test_GO_variants(ngen, rel_eq, seed=42):
    variant_info = {
        "Language": "Go",
        "Library": "",
        "System": "",
        "Compiler": "",
        "VariabilityMisc": "seed {}".format(seed),
        "NumberGenerations": ngen,
        "EqualityCheck": rel_eq, 
        }
    cmd_str = './testassoc -number {} -equality-check {}'.format(ngen, rel_eq)
    if seed is not None:
        cmd_str = cmd_str + ' -seed={}'.format(seed) 
    
    result_str = analyze_results(REPEAT, cmd_str)
    print_variant_results(variant_info, result_str)

def build_GO_variants():
    cmd_args = ["go", "build", "-o", "testassoc", "testassoc.go"]
    cmd_str = " ".join(cmd_args)
    result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error while building Go variants")
        print(result.stderr)
        exit(1)

########### Perl

def test_Perl_variants(ngen, rel_eq, seed=42):
    variant_info = {
        "Language": "Perl",
        "Library": "",
        "System": "",
        "Compiler": "",
        "VariabilityMisc": "seed {}".format(seed),
        "NumberGenerations": ngen,
        "EqualityCheck": rel_eq, 
        }
    cmd_str = 'perl testassoc.pl --number {} --equality-check {}'.format(ngen, rel_eq)
    if seed is not None:
        cmd_str = cmd_str + ' --seed={}'.format(seed) 
    
    result_str = analyze_results(REPEAT, cmd_str)
    print_variant_results(variant_info, result_str)

#################### VARIANTS execution 

print_column_names()

os.chdir("perl")

try:
    test_Perl_variants(GNUMBER_GENERATIONS, "ASSOCIATIVITY", None)
    test_Perl_variants(GNUMBER_GENERATIONS, "MULT_INV", None)
    test_Perl_variants(GNUMBER_GENERATIONS, "MULT_INV_PI", None)

    test_Perl_variants(GNUMBER_GENERATIONS, "ASSOCIATIVITY", 42)
    test_Perl_variants(GNUMBER_GENERATIONS, "MULT_INV", 42)
    test_Perl_variants(GNUMBER_GENERATIONS, "MULT_INV_PI", 42)
except Exception as e:
    print("Perl failed")
    print(e)

os.chdir("..")

os.chdir("go")

try:
    build_GO_variants()
    test_GO_variants(GNUMBER_GENERATIONS, "associativity", None)
    test_GO_variants(GNUMBER_GENERATIONS, "mult-inverse", None)
    test_GO_variants(GNUMBER_GENERATIONS, "mult-inverse-pi", None)

    test_GO_variants(GNUMBER_GENERATIONS, "associativity", 42)
    test_GO_variants(GNUMBER_GENERATIONS, "mult-inverse", 42)
    test_GO_variants(GNUMBER_GENERATIONS, "mult-inverse-pi", 42)
except Exception as e:
    print("Go failed")
    print(e)


os.chdir("..")


os.chdir("R")

try:
    test_R_variants(GNUMBER_GENERATIONS, "ASSOCIATIVITY", None)
    test_R_variants(GNUMBER_GENERATIONS, "MULT_INV", None)
    test_R_variants(GNUMBER_GENERATIONS, "MULT_INV_PI", None)

    test_R_variants(GNUMBER_GENERATIONS, "ASSOCIATIVITY", 42)
    test_R_variants(GNUMBER_GENERATIONS, "MULT_INV", 42)
    test_R_variants(GNUMBER_GENERATIONS, "MULT_INV_PI", 42)
except Exception as e:
    print("R failed")
    print(e)

os.chdir("..")

os.chdir("julia")

try:
    seqs = [True, False]
    for seq in seqs:
        test_Julia_variants(GNUMBER_GENERATIONS, "ASSOCIATIVITY", seq, None)
        test_Julia_variants(GNUMBER_GENERATIONS, "MULT_INV", seq, None)
        test_Julia_variants(GNUMBER_GENERATIONS, "MULT_INV_PI", seq, None)

        test_Julia_variants(GNUMBER_GENERATIONS, "ASSOCIATIVITY", seq, 42)
        test_Julia_variants(GNUMBER_GENERATIONS, "MULT_INV", seq, 42)
        test_Julia_variants(GNUMBER_GENERATIONS, "MULT_INV_PI", seq, 42)
except Exception as e:
    print("Julia failed")
    print(e)

os.chdir("..")  # change back to previous directory

os.chdir("cpp")

try:
    test_CPlusPlus_variants(GNUMBER_GENERATIONS, "associativity", None)
    test_CPlusPlus_variants(GNUMBER_GENERATIONS, "mult-inverse", None)
    test_CPlusPlus_variants(GNUMBER_GENERATIONS, "mult-inverse-pi", None)

    test_CPlusPlus_variants(GNUMBER_GENERATIONS, "associativity", 42)
    test_CPlusPlus_variants(GNUMBER_GENERATIONS, "mult-inverse", 42)
    test_CPlusPlus_variants(GNUMBER_GENERATIONS, "mult-inverse-pi", 42)
except Exception as e:
    print("C++ failed")
    print(e)

os.chdir("..")  # change back to previous directory

os.chdir("ocaml")
try:
    build_Ocaml_variants() # prerequiste
    test_Ocaml_variants(GNUMBER_GENERATIONS, "associativity", 42)
    test_Ocaml_variants(GNUMBER_GENERATIONS, "mult-inverse", 42)
    test_Ocaml_variants(GNUMBER_GENERATIONS, "mult-inverse-pi", 42)

    test_Ocaml_variants(GNUMBER_GENERATIONS, "associativity", None)
    test_Ocaml_variants(GNUMBER_GENERATIONS, "mult-inverse", None)
    test_Ocaml_variants(GNUMBER_GENERATIONS, "mult-inverse-pi", None)
except Exception as e:
    print("Ocaml failed")
    print(e)

os.chdir("..")  # change back to previous directory

os.chdir("swift")

try:
    build_Swift_variants() # prerequiste
    test_Swift_variants(GNUMBER_GENERATIONS, "associativity")
    test_Swift_variants(GNUMBER_GENERATIONS, "mult-inverse")
    test_Swift_variants(GNUMBER_GENERATIONS, "mult-inverse-pi")
except Exception as e:
    print("Swift failed")
    print(e)

os.chdir("..")  # change back to previous directory

os.chdir("scala")

try:
    # TODO: build once, run multiple times
    # TODO: scala-cli or other Scala environment (eg ScalaJS)
    test_Scala_variants(GNUMBER_GENERATIONS, "Associativity")
    test_Scala_variants(GNUMBER_GENERATIONS, "MultInv")
    test_Scala_variants(GNUMBER_GENERATIONS, "MultInvPi")
except Exception as e:
    print("Scala failed")
    print(e)
os.chdir("..")  # change back to previous directory

try:
    # TODO fix number of generations, Bash is quite slow
    test_BASH_variants(100, "associativity")
    test_BASH_variants(100, "mult_inverse")
    test_BASH_variants(100, "mult_inverse_pi")
except Exception as e:
    print("Bash failed")
    print(e)

try:
    test_LISP_variants(42000) # TODO: play with number of generations (proportions), default value used right now
except Exception as e:
    print("LISP failed")
    print(e)

try:
    test_JavaScript_variants("associativity", True, GNUMBER_GENERATIONS)
    test_JavaScript_variants("mult_inverse", True, GNUMBER_GENERATIONS)
    test_JavaScript_variants("mult_inverse_pi", True, GNUMBER_GENERATIONS)
    test_JavaScript_variants("associativity", False, GNUMBER_GENERATIONS)
    test_JavaScript_variants("mult_inverse", False, GNUMBER_GENERATIONS)
    test_JavaScript_variants("mult_inverse_pi", False, GNUMBER_GENERATIONS)
except Exception as e:
    print("JavaScript failed")
    print(e)

try:
    # TODO: doubt: is run building?
    test_RUST_variants("associativity", GNUMBER_GENERATIONS, "0.000000000000001")
    test_RUST_variants("mult_inverse", GNUMBER_GENERATIONS, "0.000000000000001")
    test_RUST_variants("mult_inverse_pi", GNUMBER_GENERATIONS, "0.000000000000001")
    test_RUST_variants("associativity", GNUMBER_GENERATIONS)
    test_RUST_variants("mult_inverse", GNUMBER_GENERATIONS)
    test_RUST_variants("mult_inverse_pi", GNUMBER_GENERATIONS)
except Exception as e:
    print("Rust failed")
    print(e)

try:
    test_C_variants(GNUMBER_GENERATIONS) # includes compilation and runtime variations
except Exception as e:
    print("C failed")
    print(e)

try:
    compile_JAVA_variants() # prerequisites, applies to all variants
    test_JAVA_variants("java.util.Random.nextFloat()", GNUMBER_GENERATIONS, "basic")
    test_JAVA_variants("Math.random()", GNUMBER_GENERATIONS, "math")
    test_JAVA_variants("java.util.Random.nextDouble()", GNUMBER_GENERATIONS, "double")
except Exception as e:
    print("Java failed")
    print(e)

try:
    test_PY_variants("associativity", GNUMBER_GENERATIONS)
    test_PY_variants("mult-inverse", GNUMBER_GENERATIONS)
    test_PY_variants("mult-inverse-pi", GNUMBER_GENERATIONS)

    test_PY_variants("associativity", GNUMBER_GENERATIONS, 42)
    test_PY_variants("mult-inverse", GNUMBER_GENERATIONS, 42)
    test_PY_variants("mult-inverse-pi", GNUMBER_GENERATIONS, 42)
except Exception as e:
    print("Python failed")
    print(e)


