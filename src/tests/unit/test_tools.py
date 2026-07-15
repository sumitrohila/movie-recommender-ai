from src.tools.movie_db import MovieDBTool

def test_movie_db_tool():
    tool = MovieDBTool()
    result = tool._run("1")
    assert "The Matrix" in result
    result = tool._run("Sci-Fi")
    assert "Inception" in result