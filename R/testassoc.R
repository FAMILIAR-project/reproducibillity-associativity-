#define packages to install
packages <- c('optparse')

#install all packages that are not already installed
install.packages(setdiff(packages, rownames(installed.packages())),,repos = "http://cran.us.r-project.org")
# Load required packages
library(optparse)
library(enum)

# Define an enumeration class for the EqualityCheck
EqualityCheck <- list(ASSOCIATIVITY="ASSOCIATIVITY", MULT_INV="MULT_INV", MULT_INV_PI="MULT_INV_PI")

# Define the equality test function
equality_test <- function(equality_check, x, y, z) {
  if (equality_check == EqualityCheck$ASSOCIATIVITY) {
    return(x + (y + z) == (x + y) + z)
  } else if (equality_check == EqualityCheck$MULT_INV) {
    return((x * z) / (y * z) == x / y)
  } else if (equality_check == EqualityCheck$MULT_INV_PI) {
    return((x * z * pi) / (y * z * pi) == x / y)
  }
}

# Define the proportion function
proportion <- function(number = 10000, seed_val = NULL, equality_check) {
  if (!is.null(seed_val)) {
    set.seed(seed_val)
  }
  
  ok <- 0
  
  for (i in 1:number) {
    x <- runif(1)
    y <- runif(1)
    z <- runif(1)
    
    ok <- ok + equality_test(equality_check, x, y, z)
  }
  
  return(ok * 100 / number)
}

# Define the command line arguments
option_list <- list(
  make_option(c("--seed"), type="integer", default=NULL, help="Seed value."),
  make_option(c("--number"), type="integer", default=10000, help="Number of tests"),
  make_option(c("--eq_check"), type="character") # , required=TRUE, help="Type of equality check") # , choices=as.character(EqualityCheck))
)

# Parse the command line arguments
opt_parser <- OptionParser(option_list=option_list)
opt <- parse_args(opt_parser)

# if eq_check is not in the list of choices, print an error message and exit
if (!opt$eq_check %in% as.character(EqualityCheck)) {
  cat(sprintf("Error: %s is not a valid equality check.\n", opt$eq_check))
  cat(sprintf("Choices are: %s\n", paste(as.character(EqualityCheck), collapse=", ")))
  q(status=1)
}

# Call the proportion function and print the result
result <- proportion(number=opt$number, seed_val=opt$seed, equality_check=opt$eq_check)
cat(sprintf("%f%%\n", result))
