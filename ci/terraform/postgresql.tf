provider "postgresql" {
  alias    = "ddldump"
  host     = "127.0.0.1"
  port     = 5432
  username = "ddldump"
  password = "ddldump"
  sslmode  = "disable"
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
