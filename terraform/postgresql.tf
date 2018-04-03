provider "postgresql" {
  alias    = "ddldump"
  host     = "localhost"
  port     = 10250
  username = "ddldump"
  password = "ddldump"
  sslmode  = "require"
}

# Databases

resource "postgresql_database" "ddldump-ddldump" {
  provider = "postgresql.ddldump"
  name     = "ddldump"
}

# Roles

resource "postgresql_role" "ddldump-ddldump_test" {
  provider = "postgresql.ddldump"
  name     = "ddldump_test"
  login    = true
}
