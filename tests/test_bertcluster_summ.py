# pylint: skip-file
import numpy as np
import pytest


@pytest.mark.skip()
def test_bert_cluster_model():
    tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-base-turkish-cased")  # noqa: F821
    model = BertModel.from_pretrained("dbmdz/bert-base-turkish-cased", output_hidden_states=True)  # noqa: F821

    summarizer = AnnotatedExtractiveSummarizer(tokenizer, model, k=4, layers=[11], random_state=42,  # noqa: E126 F821
                                               doEval=True)

    jfile = '../work/Labeled/bitmemis-evlilikler-375881_labeled.json'

    summary = summarizer.summarize(jfile)

    assert np.unique(summary == np.array(
        ['Kadın ve erkek evliliklerini bitirirler, bazen kadın, bazen erkek bazen de aynı anda boşanma kararı alırlar.',
         ('Boşanmanın üzerinden biraz zaman geçince taraflardan biri (çoğu zaman erkek) eski eşinin yeni '
          'bir hayata başlamasına, yeni insanlarla görüşme ihtimaline bile dayanamaz.'),
         'Basit olarak diyebiliriz ki aynı doğadaki gibi dişi, hayatta kalma konusunda daha başarılıdır.',
         ('Boşanmanıza rağmen eski eşinize ‘Eski’ derken hala diliniz sürçüyorsa, zorlanıyorsanız, bitmemiş hesaplar, '
          'öyküler, eskiye dair takılıp kalmalar varsa, kendinizi onun evininin önünde buluyorsanız, '
          'evinin ışığını kontrol ediyor, içeride olanları merak ediyorsanız, kapısını çalıyorsanız, '
          'orada kalmak istiyorsanız, hayatına müdahale etmek istiyorsanız, kıskanıyorsanız, boşanmanın '
          'üzerinden yıllar geçmesine rağmen hayatınıza yeni birini almayı reddediyorsanız ya da alamıyorsanız, '
          'buna benzer süreçler yaşıyorsanız gerçekte boşanmamışsınız anlamına gelebilir.')],
        dtype='<U559'))[0]


@pytest.mark.skip()
def test_bert_cluster_scorer():
    tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-base-turkish-cased")  # noqa: F821
    model = BertModel.from_pretrained("dbmdz/bert-base-turkish-cased", output_hidden_states=True)  # noqa: F821

    summarizer = AnnotatedExtractiveSummarizer(tokenizer, model, k=4, layers=[11], random_state=42,  # noqa: E126 F821
                                               doEval=True)

    jfile = '../work/Labeled/bitmemis-evlilikler-375881_labeled.json'

    _ = summarizer.summarize(jfile)

    assert summarizer.score().astype(np.float16) == np.float16(0.2433)
