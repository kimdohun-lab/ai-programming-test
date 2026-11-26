import csv
import importlib
import sys
from pathlib import Path

import pytest

# Ensure the project root is importable when this test is run directly.
sys.path.insert(0, str(Path(__file__).resolve().parent))

load_scores = importlib.import_module("week11.load_scores").load_scores


def test_valid_rows_are_returned_with_trimmed_names_and_integer_scores(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(
        "이름,점수\n 민지 , 85 \n지훈,0\n하늘,100\n",
        encoding="utf-8",
    )
    original = csv_file.read_bytes()

    kept, skipped = load_scores(csv_file)

    assert kept == [("민지", 85), ("지훈", 0), ("하늘", 100)]
    assert skipped == []
    assert csv_file.read_bytes() == original


@pytest.mark.parametrize("score", [-1, 101])
def test_scores_outside_inclusive_range_are_reported(tmp_path, score):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(f"이름,점수\n학생,{score}\n", encoding="utf-8")

    kept, skipped = load_scores(csv_file)

    assert kept == []
    assert skipped == [(2, f"학생,{score}", "점수가 0~100 밖")]


def test_invalid_rows_are_skipped_with_physical_line_numbers_and_reasons(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(
        "이름,점수\n"
        "열하나만\n"
        "학생,80,추가\n"
        ",90\n"
        "   ,90\n"
        "학생,\n"
        "학생,점수없음\n"
        "학생,90.5\n"
        "학생,-1\n"
        "학생,101\n"
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
        (5, "   ,90", "이름이 비어 있음"),
        (6, "학생,", "점수가 비어 있음"),
        (7, "학생,점수없음", "점수가 정수가 아님"),
        (8, "학생,90.5", "점수가 정수가 아님"),
        (9, "학생,-1", "점수가 0~100 밖"),
        (10, "학생,101", "점수가 0~100 밖"),
    ]


def test_invalid_header_is_rejected(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text("학생,점수\n민지,85\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_scores(csv_file)


def test_duplicate_name_is_skipped_and_reported(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(
        "이름,점수\n민지,85\n민지,90\n지훈,80\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(csv_file)

    assert kept == [("민지", 85), ("지훈", 80)]
    assert skipped == [(3, "민지,90", "이름이 중복됨")]


def test_quoted_comma_and_multiline_name_are_parsed_as_single_fields(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(
        '이름,점수\n"김,민",80\n"두 줄\n이름",90\n,70\n',
        encoding="utf-8",
    )

    kept, skipped = load_scores(csv_file)

    assert kept == [("김,민", 80), ("두 줄\n이름", 90)]
    assert skipped == [(5, ",70", "이름이 비어 있음")]


def test_malformed_quoting_raises_csv_error(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text('이름,점수\n"학생,80\n', encoding="utf-8")

    with pytest.raises(csv.Error):
        load_scores(csv_file)


def test_header_only_file_returns_empty_results(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text("이름,점수\n", encoding="utf-8")

    assert load_scores(csv_file) == ([], [])


def test_missing_file_raises_file_not_found_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "missing.csv")