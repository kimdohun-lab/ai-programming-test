# ai-programming-test
import pytest

from week11.load_scores import load_scores


def test_valid_rows_are_kept_and_names_and_scores_are_stripped(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(
        "이름,점수\n 민지 , 85 \n지훈,90\n민지,85\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(csv_file)

    assert kept == [("민지", 85), ("지훈", 90), ("민지", 85)]
    assert skipped == []


@pytest.mark.parametrize("score", [0, 100])
def test_score_boundaries_are_valid(tmp_path, score):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(f"이름,점수\n학생,{score}\n", encoding="utf-8")

    kept, skipped = load_scores(csv_file)

    assert kept == [("학생", score)]
    assert skipped == []


@pytest.mark.parametrize("score", [-1, 101])
def test_scores_outside_boundaries_are_skipped(tmp_path, score):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(f"이름,점수\n학생,{score}\n", encoding="utf-8")

    kept, skipped = load_scores(csv_file)

    assert kept == []
    assert skipped == [(2, f"학생,{score}", "점수가 0~100 밖")]


def test_invalid_rows_are_skipped_with_reasons_and_line_numbers(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(
        "이름,점수\n"
        "열하나만\n"
        "학생,80,추가\n"
        ",90\n"
        "학생,\n"
        "학생,90.5\n"
        "학생,-1\n"
        "\n"
        " 정상 , 75 \n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(csv_file)

    assert kept == [("정상", 75)]
    assert skipped == [
        (2, "열하나만", "열 개수가 2가 아님"),
        (3, "학생,80,추가", "열 개수가 2가 아님"),
        (4, ",90", "이름이 비어 있음"),
        (5, "학생,", "점수가 비어 있음"),
        (6, "학생,90.5", "점수가 정수가 아님"),
        (7, "학생,-1", "점수가 0~100 밖"),
    ]


@pytest.mark.parametrize("contents", ["이름,점수\n", "이름,점수\n\n"])
def test_header_only_and_blank_rows_return_empty_lists(tmp_path, contents):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(contents, encoding="utf-8")

    assert load_scores(csv_file) == ([], [])


def test_utf8_bom_is_accepted(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_bytes("이름,점수\n학생,100\n".encode("utf-8-sig"))

    kept, skipped = load_scores(csv_file)

    assert kept == [("학생", 100)]
    assert skipped == []


def test_empty_file_returns_empty_lists(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_bytes(b"")

    assert load_scores(csv_file) == ([], [])


def test_missing_file_raises_file_not_found_error(tmp_path):
    with pytest.raises(FileNotFoundError):
<<<<<<< Updated upstream
        load_scores(tmp_path / "missing.csv")
=======
        load_scores(tmp_path / "missing.csv")
>>>>>>> Stashed changes
