import ArgumentParser
import Foundation
@main 
struct TestAssoc: ParsableCommand {
    //static let configuration = CommandConfiguration(abstract: "Equality test with seed.")
    
    @Option(name: .shortAndLong, help: "Seed value.")
    var seed: Int?
    
    @Option(name: .shortAndLong, help: "Number of tests.")
    var number: Int = 10000
    
    @Option(name: .shortAndLong, help: "Type of equality check.") // , completion: .values(EqualityCheck.allCases.map(\.rawValue)))
    var equalityCheck: EqualityCheck
    
    func run() throws {
        print("\(proportion(number: number, seedVal: seed ?? Int(Date().timeIntervalSince1970), equalityCheck: equalityCheck))%")
    }


    enum EqualityCheck: String, ExpressibleByArgument {
    case associativity = "associativity"
    case multInv = "mult-inverse"
    case multInvPi = "mult-inverse-pi"
}

func equalityTest(equalityCheck: EqualityCheck, x: Double, y: Double, z: Double) -> Bool {
    switch equalityCheck {
    case .associativity:
        return x + (y + z) == (x + y) + z
    case .multInv:
        return (x * z) / (y * z) == x / y
    case .multInvPi:
        return (x * z * Double.pi) / (y * z * Double.pi) == (x / y)
    }
}

func proportion(number: Int, seedVal: Int, equalityCheck: EqualityCheck) -> Int {
    var ok = 0
    srand(UInt32(seedVal))
    for _ in 0..<number {
        let x = Double(rand()) / Double(RAND_MAX)
        let y = Double(rand()) / Double(RAND_MAX)
        let z = Double(rand()) / Double(RAND_MAX)
        ok += equalityTest(equalityCheck: equalityCheck, x: x, y: y, z: z) ? 1 : 0
    }
    return ok * 100 / number
}
}









