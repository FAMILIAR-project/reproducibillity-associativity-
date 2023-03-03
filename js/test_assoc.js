const { ArgumentParser } = require('argparse');
const seedrandom = require('seedrandom');

const EqualityCheck = Object.freeze({
  ASSOCIATIVITY: "associativity",
  MULT_INVERSE: "mult_inverse",
  MULT_INVERSE_PI: "mult_inverse_pi",
});

function associativityTest(option) {
  const x = Math.random();
  const y = Math.random();
  const z = Math.random();
  if (option === EqualityCheck.ASSOCIATIVITY) {
    return x + (y + z) === (x + y) + z;
  } else if (option === EqualityCheck.MULT_INVERSE) {
    return (x * z) / (y * z) === x / y;
  } else if (option === EqualityCheck.MULT_INVERSE_PI) {
    const pi = Math.PI;
    return (x * z * pi) / (y * z * pi) === x / y;
  } else {
    throw new Error("Invalid option");
  }
}

function proportion(number, seedVal, option) {
  const rng = seedrandom(seedVal);
  let ok = 0;
  for (let i = 0; i < number; i++) {
    ok += associativityTest(option);
  }
  return (ok * 100) / number;
}

const parser = new ArgumentParser({
  description: 'Associativity test with seed.',
});

parser.add_argument('--seed', { type: Number, required: true, help: 'Seed value' });
parser.add_argument('--number', { type: Number, default: 10000, help: 'Number of tests' });
parser.add_argument('--equality-check', { choices: Object.values(EqualityCheck), default: EqualityCheck.ASSOCIATIVITY, help: 'Type of equality check (associativity, mult_inverse, mult_inverse_pi)' });
const args = parser.parse_args();

console.log(`${proportion(args.number, args.seed, args.equality_check)}%`);
