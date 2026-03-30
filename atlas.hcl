env "docker" {
  url = getenv("ATLAS_DATABASE_URL")

  migration {
    dir = "file://migrations"
  }
}
