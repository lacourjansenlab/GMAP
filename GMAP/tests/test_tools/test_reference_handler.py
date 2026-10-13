"""
tests missing:

(@ December 4th '24):
 (0 missed statements)

- None!

"""

# 3rd party imports
import pytest

# local imports
import GMAP.src.tools.coding_tools as GM_ct
import GMAP.src.tools.exceptions as GM_ex
import GMAP.src.tools.print_tools as GM_pt
import GMAP.src.tools.reference_handler as GM_rh


class TestReference:
    def test_input_string(self):
        ref = GM_rh.Reference(get_reference_string1())
        assert ref.success is True
        assert ref.input_string == get_reference_string1()
        assert ref.title == "A very cool paper"
        assert ref.author_raw == [
            ["LastName1", "Steve"], ["LastName2", "Erik"]]
        assert ref.author == ["LastName1, S.", "LastName2, E."]
        assert ref.year == "1752"
        assert ref.journal == "Best Journal"
        assert ref.volume == "42"
        assert ref.pages == "666"
        assert not hasattr(ref, "issn")
        assert ref.doi == "DOIcode"
        assert ref.url == "https://coolwebsite.com"
        assert ref.mapkey == ["coolpaper"]
        assert ref.reporttext == {"dip": ["dipole moment of Cool", "hello!"]}

    def test_input_string_broken(self):
        ref = GM_rh.Reference(get_reference_string_broken1())
        assert ref.success is False

        ref = GM_rh.Reference(get_reference_string_broken2())
        assert ref.success is False

    def test_eq(self):
        # two separate instances, but same contents.
        assert GM_rh.Reference(get_reference_string1()) == (
            GM_rh.Reference(get_reference_string1())
        )

    def test_str(self):
        ref = GM_rh.Reference(get_reference_string1())
        assert str(ref) == (
            'LastName1, S.; LastName2, E.. "A very cool paper". In Best '
            "Journal vol. 42 (1752), p. 666, doi: DOIcode, "
            "url: https://coolwebsite.com"
        )

        ref = GM_rh.Reference(get_reference_string2())
        assert str(ref) == (
            'LastName2, S.; LastName1, E.. "A very cool paper". In Best '
            "Journal 42.2 (Aug 1752), pp. 666-777, doi: DOIcode, "
            "url: https://coolwebsite2.com"
        )

        ref = GM_rh.Reference(get_reference_string3())
        assert str(ref) == (
            'This, A.; Paper, B.; Has, C.; Very, D.; Many, E. et al. "A very'
            ' cool paper". In Best Journal'
            " no. 2 (1752), p. 666, doi: DOIcode, "
            "url: https://coolwebsite3.com"
        )

        ref = GM_rh.Reference(get_reference_string_bare())
        assert str(ref) == (
            "unknown author. unknown title. In unknown journal vol. unknown "
            "(unknown year), issn: only an ISSN"
        )


def test_read_reference_file(tmp_path):
    two_ref_string = (
        get_reference_string1() + "\n" + get_reference_string2()
        + "\n" + get_reference_string3())
    with open(tmp_path / "reffile.txt", "w") as fhand:
        fhand.write(two_ref_string)

    allrefs = GM_rh.read_reference_file(tmp_path / "reffile.txt")
    assert allrefs == {
        "coolpaper": [
            GM_rh.Reference(get_reference_string1()),
            GM_rh.Reference(get_reference_string3())],
        "coolpaper2": [GM_rh.Reference(get_reference_string2())]}


def test_report_references(capsys):
    run_pars = GM_ct.CustomClass(**{"output_data": ["dip", "ham"]})
    references = [
        GM_rh.Reference(get_reference_string1()),
        GM_rh.Reference(get_reference_string2()),
        GM_rh.Reference(get_reference_string3())]

    GM_pt.Printer.set_state("running")
    GM_rh.report_references(run_pars, references)
    captured = capsys.readouterr()
    assert captured.out.endswith(
        "The following reference was used for calculating the:\n"
        " - dipole moment of Cool\n"
        " - hello!\n" +
        GM_pt.word_wrap(str(GM_rh.Reference(get_reference_string1()))) +
        "\n\nThe following reference was used for calculating the:\n"
        " - dipole moment of Cool\n"
        " - hello!\n" +
        GM_pt.word_wrap(str(GM_rh.Reference(get_reference_string2()))) +
        "\n\nThe following reference was used for calculating the:\n"
        " - dipole moment of Cool\n"
        " - hello!\n" +
        GM_pt.word_wrap(str(GM_rh.Reference(get_reference_string3()))) + "\n\n"
    )


def test_flatten_iterable():
    ref = GM_rh.Reference(get_reference_string1())
    assert GM_rh.flatten_iterable(ref) == [ref]
    assert GM_rh.flatten_iterable([ref]) == [ref]
    assert GM_rh.flatten_iterable({"x": ref}) == [ref]
    with pytest.raises(GM_ex.GmapTypeError):
        assert GM_rh.flatten_iterable("x") == [ref]
    assert GM_rh.flatten_iterable([[ref]]) == [ref]
    assert GM_rh.flatten_iterable({"x": [ref]}) == [ref]
    assert GM_rh.flatten_iterable([{"x": ref}]) == [ref]
    assert GM_rh.flatten_iterable([ref, [ref]]) == [ref, ref]
    with pytest.raises(GM_ex.GmapTypeError):
        assert GM_rh.flatten_iterable([["x"]]) == [ref]


def get_reference_string1():
    return (
        "@article{MyCoolArticle,\n"
        "    title = {A very cool paper},\n"
        "    author = {LastName1, Steve and LastName2, Erik},\n"
        "    year = {1752},\n"
        "    journal = {Best Journal},\n"
        "    volume = {42},\n"
        "    pages = {666},\n"
        "    doi = {DOIcode},\n"
        "    url = {https://coolwebsite.com},\n"
        "    langid = {english},\n"
        "    mapkey = {coolpaper},\n"
        "    reporttext = {dip: dipole moment of Cool; dip: hello!}\n"
        "}"
    )


def get_reference_string2():
    return (
        "@article{MyCoolArticle,\n"
        "    title = {A very cool paper},\n"
        "    author = {LastName2, Steve and LastName1, Erik},\n"
        "    year = {1752},\n"
        "    month = Aug,\n"
        "    journal = {Best Journal},\n"
        "    volume = {42},\n"
        "    number = {2},\n"
        "    pages = {666-777},\n"
        "    doi = {DOIcode},\n"
        "    url = {https://coolwebsite2.com},\n"
        "    langid = {english},\n"
        "    mapkey = {coolpaper2},\n"
        "    reporttext = {dip: dipole moment of Cool; dip: hello!}\n"
        "}"
    )


def get_reference_string3():
    return (
        "@article{MyCoolArticle,\n"
        "    title = {A very cool paper},\n"
        "    author = {This, Alfred and Paper, Bart and Has, Charlie and "
        "Very, David and Many, Edward and Authors, Frank},\n"
        "    year = {1752},\n"
        "    journal = {Best Journal},\n"
        "    number = {2},\n"
        "    pages = {666},\n"
        "    doi = {DOIcode},\n"
        "    url = {https://coolwebsite3.com},\n"
        "    langid = {english},\n"
        "    mapkey = {coolpaper},\n"
        "    reporttext = {dip: dipole moment of Cool; dip: hello!}\n"
        "}"
    )


def get_reference_string_bare():
    return (
        "@article{ISSNarticle,\n"
        "    issn = {only an ISSN},\n"
        "    mapkey = {ISSNpaper},\n"
        "    reporttext = {dip: dipole moment of ISSN}\n"
        "}"
    )


def get_reference_string_broken1():
    return (
        "@article{ISSNarticle,\n"
        "    issn\n"
        "    mapkey = {ISSNpaper},\n"
        "    reporttext = {dip: dipole moment of ISSN}\n"
        "}"
    )


def get_reference_string_broken2():
    return (
        "@article{ISSNarticle,\n"
        "    issn = {only an ISSN},\n"
        "    reporttext = {dip: dipole moment of ISSN}\n"
        "}"
    )
