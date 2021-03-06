import numpy as np
import torch
import pytest
from pytest import raises
from scipy.sparse import isspmatrix_csr
from .context import Doc, BertTokenizer, SimpleTokenizer, tokenizer_context, tf_context, config_context


@pytest.mark.parametrize("string", ["", " ", "\n", "\t", "\n\t"])
def test_emptystring(string):
    empty = Doc(string)

    assert len(empty.sents) == 1
    assert len(empty[0].tokens) == 0


@pytest.mark.parametrize("tokenizer", [BertTokenizer.__name__, SimpleTokenizer.__name__])
def test_tokens(tokenizer):
    with tokenizer_context(tokenizer) as Doc2:
        d = Doc2("Ali topu tut. Ömer ılık süt iç.")

        with pytest.warns(DeprecationWarning):
            s0 = d.sents[0]

        assert s0.tokens == ['Ali', 'topu', 'tut', '.']

        assert s0.tokens_with_special_symbols == ['[CLS]', 'Ali', 'topu', 'tut', '.', '[SEP]']


@pytest.mark.parametrize("tokenizer", [BertTokenizer.__name__, SimpleTokenizer.__name__])
def test_bert_embedding_generation(tokenizer):
    with tokenizer_context(tokenizer) as Doc2:

        d = Doc2("Ali topu tut. Ömer ılık süt iç.")

        if tokenizer == SimpleTokenizer.__name__:
            with raises(NotImplementedError):
                assert d.bert_embeddings.shape == (2, 768)
        else:
            assert d.bert_embeddings.shape == (2, 768)


@pytest.mark.parametrize('tf_type', ['binary', 'raw', 'freq', 'log_norm', 'double_norm'])
def test_tfidf_embedding_generation(tf_type):
    with tf_context(tf_type):
        d = Doc("Ali topu tut. Ömer ılık süt iç.")
        assert d.tfidf_embeddings.shape == (2, d.vocabulary.size)


@pytest.mark.parametrize('tf_type', ['binary', 'raw', 'freq', 'log_norm', 'double_norm'])
def test_tfidf_compare_doc_and_sent(tf_type):
    with tf_context(tf_type):
        d = Doc("Ali topu tut. Ömer ılık süt iç.")

        for i, sent in enumerate(d.sents):
            assert np.all(np.isclose(d.tfidf_embeddings.toarray()[i, :], sent.tfidf()))


testdata = [(True, True),
            (True, False),
            (False, False),
            (False, True)]


@pytest.mark.parametrize("return_numpy, return_mask", testdata)
def test_padded_matrix(return_numpy, return_mask):
    d = Doc("Ali topu tut. Ömer ılık süt iç.")

    inp = np.array([[2, 3744, 9290, 2535, 18, 3, 0],
                    [2, 6565, 17626, 5244, 2032, 18, 3]])

    mask = np.array([[1, 1, 1, 1, 1, 1, 0],
                     [1, 1, 1, 1, 1, 1, 1]])

    res = d.padded_matrix(return_numpy, return_mask)

    if return_numpy:
        if return_mask:
            assert np.all(res[0] == inp)
            assert np.all(res[1] == mask)
        else:
            assert np.all(res == inp)
    else:
        if return_mask:
            assert torch.all(res[0] == torch.tensor(inp))  # noqa # pylint: disable=not-callable
            assert torch.all(res[1] == torch.tensor(mask))  # noqa # pylint: disable=not-callable
        else:
            assert torch.all(res == torch.tensor(inp))  # noqa # pylint: disable=not-callable


@pytest.mark.parametrize("test_for", ["text", "str", "strall"])
def test_span(test_for):
    d = Doc("Ali   topu  tut.")

    spans = d.spans

    if test_for == "text":
        assert [s.text for s in spans] == ['Ali', 'topu', 'tut.']

    elif test_for == "str":
        assert [str(s) for s in spans] == ['Ali', 'topu', 'tut.']
    else:
        assert str(spans) == "[Ali, topu, tut.]"


def test_doc_with_no_sentence():
    raw = "söz konusu adreste bulunan yolda yağmurdan dolayı çamur ve toprak bulunmaktadır"

    d = Doc(raw)

    with pytest.warns(DeprecationWarning):
        assert d.sents[0].tokens == Doc.from_sentences([("söz konusu adreste bulunan yolda yağmurdan "
                                                         "dolayı çamur ve toprak bulunmaktadır")]).sents[0].tokens


def test_doc_index():
    d = Doc("Ali topu tut. Ömer ılık süt iç.")

    assert d[0] == "Ali topu tut."


def test_doc_iter_next():
    d = Doc("Ali topu tut. Ömer ılık süt iç.")

    assert next(iter(d)) == "Ali topu tut."


def test_doc_iter_eq():
    d = Doc("Ali topu tut. Ömer ılık süt iç.")

    for i, sentence in enumerate(d):
        assert d._sents[i] == sentence == d[i]


def test_doc_level_tfidf():
    d = Doc("Ali topu tut. Ömer ılık süt iç.")
    assert d.tfidf().shape == (1, d.vocabulary.size)


def test_doc_level_tf_idf_value():
    with config_context(tf__method="binary") as Doc_c:
        d = Doc_c("Ali topu tut. Ömer ılık süt iç.")
        assert np.sum(d.tfidf().toarray()) == pytest.approx(31.938)


def test_doc_level_tf_idf_type():
    d = Doc("Ali topu tut. Ömer ılık süt iç.")
    assert isspmatrix_csr(d.tfidf())
