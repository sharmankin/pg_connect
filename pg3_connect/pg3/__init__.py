import dotenv

dotenv.load_dotenv(
    dotenv.find_dotenv('project.env', raise_error_if_not_found=True)
)
