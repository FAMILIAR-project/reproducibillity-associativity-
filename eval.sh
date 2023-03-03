#!/bin/sh

# TODO: repeat N times the experiments and report std/mean/min/max in the Score

# TODO number as a column 

CSV_SEPARATOR=','
echo "Language${CSV_SEPARATOR}Library${CSV_SEPARATOR}System${CSV_SEPARATOR}Compiler${CSV_SEPARATOR}VariabilityMisc${CSV_SEPARATOR}Score"

echo -n "Python${CSV_SEPARATOR}std${CSV_SEPARATOR}-${CSV_SEPARATOR}-${CSV_SEPARATOR}-${CSV_SEPARATOR}" # TODO python version
python testassoc.py --seed 42 --number 1000 | tr -d '\n' # play with number 
echo "" 

javac -d . *.java
echo -n "Java${CSV_SEPARATOR}"
echo -n "java.util.Random.nextFloat()${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}-${CSV_SEPARATOR}-${CSV_SEPARATOR}" # TODO JDK version
java assoc.TestAssoc basic 1000 | tr -d '\n' # play with number (and seed TODO)
echo ""

echo -n "Java${CSV_SEPARATOR}"
echo -n "Math.random()${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}-${CSV_SEPARATOR}-${CSV_SEPARATOR}" # TODO JDK version
java assoc.TestAssoc math 1000 | tr -d '\n' # play with number
echo ""

echo -n "Java${CSV_SEPARATOR}"
echo -n "java.util.Random.nextDouble()${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}-${CSV_SEPARATOR}-${CSV_SEPARATOR}" # TODO JDK version
java assoc.TestAssoc double 1000 | tr -d '\n' # play with number
echo ""


COMPILERS=("gcc" "clang") # TODO: specific flag of clang/gcc like -ffast-math -funsafe-math-optimizations -frounding-math -fsignaling-nans; gcc/clang version
OPTIONS=("-DCUSTOM=1" "" "-DWIN=1 -DCUSTOM=1" "-DWIN=1")
FLAGS=("-DOLD_MAIN_C=1" "")

for compiler in "${COMPILERS[@]}"; do
    for i in {0..3}; do
        for flag in "${FLAGS[@]}"; do
            echo -n "C${CSV_SEPARATOR}"
            case "$i" in
                0)
                    echo -n "custom${CSV_SEPARATOR}Linux${CSV_SEPARATOR}"
                    ;;
                1)
                    echo -n "(srand48+rand48)${CSV_SEPARATOR}Linux${CSV_SEPARATOR}"
                    ;;
                2)
                    echo -n "custom${CSV_SEPARATOR}Windows${CSV_SEPARATOR}"
                    ;;
                3)
                    echo -n "(srand+rand)${CSV_SEPARATOR}Windows${CSV_SEPARATOR}"
                    ;;
            esac

            echo -n "$compiler${CSV_SEPARATOR}"
            echo -n "$flag${CSV_SEPARATOR}" # variability misc
            $compiler -o testassoc testassoc.c ${OPTIONS[$i]} ${flag}
            ./testassoc | tr -d '\n' # play with number of generations (proportions), default value used right now
            echo ""
        done
    done
done


echo -n "Rust${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}-${CSV_SEPARATOR}associativity --error_margin 0.000000000000001${CSV_SEPARATOR}" # TODO Rust-specific
cargo run --features associativity -q -- --error_margin 0.000000000000001 | tr -d '\n' # play with number
echo ""

echo -n "Rust${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}-${CSV_SEPARATOR}mult_inverse --error_margin 0.000000000000001${CSV_SEPARATOR}" # TODO Rust-specific
cargo run --features mult_inverse -q -- --error_margin 0.000000000000001 | tr -d '\n' # play with number
echo ""

echo -n "Rust${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}-${CSV_SEPARATOR}mult_inverse_pi --error_margin 0.000000000000001${CSV_SEPARATOR}" # TODO Rust-specific
cargo run --features mult_inverse_pi -q -- --error_margin 0.000000000000001 | tr -d '\n' # play with number
echo ""

echo -n "Rust${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}-${CSV_SEPARATOR}associativity (no error margin ie pure equality)${CSV_SEPARATOR}" # TODO Rust-specific
cargo run --features associativity -q -- | tr -d '\n' # play with number
echo ""

echo -n "Rust${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}-${CSV_SEPARATOR}mult_inverse (no error margin ie pure equality)${CSV_SEPARATOR}" # TODO Rust-specific
cargo run --features mult_inverse -q -- | tr -d '\n' # play with number
echo ""

echo -n "Rust${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}-${CSV_SEPARATOR}mult_inverse_pi (no error margin ie pure equality)${CSV_SEPARATOR}" # TODO Rust-specific
cargo run --features mult_inverse_pi -q -- | tr -d '\n' # play with number
echo ""

echo -n "LISP${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}"
echo -n "-${CSV_SEPARATOR}-${CSV_SEPARATOR}-${CSV_SEPARATOR}" # TODO LISP specific
sbcl --noinform --quit --load test_assoc.lisp | tr -d '\n' # play with number
echo ""

SEED="42"

function run_JStest() {
  local check="$1"
  local with_gseed="$2"

  echo -n "JavaScript${CSV_SEPARATOR}"
  echo -n "-${CSV_SEPARATOR}"
  if [[ "$with_gseed" = true ]]; then
    echo -n "-${CSV_SEPARATOR}-${CSV_SEPARATOR}${check} global seed${CSV_SEPARATOR}"
  else
    echo -n "-${CSV_SEPARATOR}-${CSV_SEPARATOR}${check}${CSV_SEPARATOR}"
  fi
  
  
  local npm_args=(--prefix js/ --silent -- --equality-check "${check}" --seed "${SEED}")
  if [[ "$with_gseed" = true ]]; then
    npm_args+=(--with-gseed)
  fi
  
  npm start "${npm_args[@]}" | tr -d '\n'
  
  echo ""
}

run_JStest "associativity" true
run_JStest "mult_inverse" true
run_JStest "mult_inverse_pi" true
run_JStest "associativity" false
run_JStest "mult_inverse" false
run_JStest "mult_inverse_pi" false

# TODO: playing with npm version and randomseed version!





