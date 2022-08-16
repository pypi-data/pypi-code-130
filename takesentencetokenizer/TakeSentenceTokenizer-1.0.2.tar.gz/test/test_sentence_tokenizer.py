import unittest
from SentenceTokenizer import SentenceTokenizer
class TestSentenceTokenizer(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tokenizer = SentenceTokenizer()

    def call_sentence_tokenizer(func):
        def inner(self, message, expected_message, use_split, sentence_tokenizer_function):
            processed_message = sentence_tokenizer_function(message.split()) if use_split else sentence_tokenizer_function(message)
            func(self, ' '.join(processed_message), expected_message) if use_split else func(self, processed_message, expected_message)
        return inner

    @call_sentence_tokenizer
    def assert_equal(self, processed_message, expected_message):
        assert processed_message == expected_message, 'Processed message "{}" is different from the expected "{}"!'.format(processed_message, expected_message)

    def test_lowercase_first_word(self):
        self.assert_equal('Bom dia', 'bom dia', True, self.tokenizer.lowercase_first_word)
        self.assert_equal('BOM DIA', 'BOM DIA', True, self.tokenizer.lowercase_first_word)
        self.assert_equal('Blip', 'blip', True, self.tokenizer.lowercase_first_word)

    def test_lowercase_caps_lock(self):
        self.assert_equal('BOM DIA', 'bom dia', True, self.tokenizer.lowercase_caps_lock)
        self.assert_equal('BOM dia', 'bom dia', True, self.tokenizer.lowercase_caps_lock)
        self.assert_equal('bom DIA', 'bom dia', True, self.tokenizer.lowercase_caps_lock)
        self.assert_equal('E', 'e', True, self.tokenizer.lowercase_caps_lock)
        self.assert_equal('OLÁ TUDO BEM COM VOCÊS???', 'olá tudo bem com vocês???', True, self.tokenizer.lowercase_caps_lock)
        self.assert_equal('será HOJE mesmo?', 'será hoje mesmo?', True, self.tokenizer.lowercase_caps_lock)

    def test_add_space_punctuation(self):
        self.assert_equal('Olá!', 'Olá !', True, self.tokenizer.add_space_punctuation)
        self.assert_equal('mas pq?', 'mas pq ?', True, self.tokenizer.add_space_punctuation)
        self.assert_equal('é mesmo!?', 'é mesmo! ?', True, self.tokenizer.add_space_punctuation)

    def test_replace_words_in_sentence(self):
        self.__regex_laugh()
        self.__regex_date()
        self.__regex_time()
        self.__regex_ddd()
        self.__regex_measure()
        self.__regex_code()
        self.__regex_phone()
        self.__regex_cnpj()
        self.__regex_cpf()
        self.__regex_email()
        self.__regex_money()
        self.__regex_url()
        self.__regex_number()
        self.__regex_emoji()

    def __regex_laugh(self):
        self.assert_equal('hahahaah', 'LAUGH', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('hehehehe', 'LAUGH', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('hehhehee', 'LAUGH', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('hihi', 'LAUGH', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('rsrsrs', 'LAUGH', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('hahah rsrsr', 'LAUGH LAUGH', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('rsrsrsrssrrsrsrsrsrsrsrsr', 'LAUGH', True, self.tokenizer.replace_words_in_sentence)

    def __regex_date(self):
        self.assert_equal('no dia 17/05', 'no dia DATE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('no dia 7/5', 'no dia DATE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('no dia 17/05/15', 'no dia DATE', True,self.tokenizer.replace_words_in_sentence)
        self.assert_equal('no dia 17/5/2015', 'no dia DATE', True,self.tokenizer.replace_words_in_sentence)
        self.assert_equal('no dia 7/5/15', 'no dia DATE', True,self.tokenizer.replace_words_in_sentence)
        self.assert_equal('no dia 17/05/2015', 'no dia DATE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('no dia 17-05', 'no dia DATE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('no dia 17-05-2015', 'no dia DATE', True, self.tokenizer.replace_words_in_sentence)

    def __regex_time(self):
        self.assert_equal('às 14:00', 'às TIME', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('às 4:00', 'às TIME', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('às 3:2', 'às TIME', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('às 4h', 'às TIME', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('às 4hrs', 'às TIME', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('às 3h2min', 'às TIME', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('às 1h21min', 'às TIME', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('às 13h21min', 'às TIME', True, self.tokenizer.replace_words_in_sentence)

    def __regex_ddd(self):
        self.assert_equal('é (043)', 'é DDD', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('é (31)', 'é DDD', True, self.tokenizer.replace_words_in_sentence)

    def __regex_measure(self):
        self.assert_equal('uns 10m', 'uns MEASURE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('uns 100km', 'uns MEASURE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('uns 100kg', 'uns MEASURE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('uns 100mg', 'uns MEASURE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('uns 100gb', 'uns MEASURE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('uns 12878397578499465467577794479gb', 'uns MEASURE', True, self.tokenizer.replace_words_in_sentence)

    def __regex_code(self):
        self.assert_equal('seria p2', 'seria CODE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('seria 2zos', 'seria CODE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('seria p2sjkfsf', 'seria CODE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('seria 2zdjgjjgnd', 'seria CODE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('seria jhjdfhjh39594lsjs', 'seria CODE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('seria 7915474864hbhf289783457642476472387379534', 'seria CODE', True, self.tokenizer.replace_words_in_sentence)

    def __regex_phone(self):
        self.assert_equal('meu número (021)33020043', 'meu número PHONE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('meu número (021)3302-0043', 'meu número PHONE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('meu número 3302-0043', 'meu número PHONE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('meu número 330450043', 'meu número PHONE', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('meu número (021)996765040', 'meu número PHONE', True, self.tokenizer.replace_words_in_sentence)

    def __regex_cnpj(self):
        self.assert_equal('empresa 31.749.397/0001-42', 'empresa CNPJ', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('empresa 32.451.843/0001-09', 'empresa CNPJ', True, self.tokenizer.replace_words_in_sentence)

    def __regex_cpf(self):
        self.assert_equal('meu cpf é 026.842.900-67', 'meu cpf é CPF', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('meu cpf é 172.644.820-73', 'meu cpf é CPF', True, self.tokenizer.replace_words_in_sentence)

    def __regex_email(self):
        self.assert_equal('email é tks@gmail.com', 'email é EMAIL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('email é tks@gmail.com.br', 'email é EMAIL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('email é take@hotmail.com', 'email é EMAIL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('email é take@outlook.com', 'email é EMAIL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('email é take_tks@outlook.com', 'email é EMAIL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('email é take_tks_research@gmail.com', 'email é EMAIL', True, self.tokenizer.replace_words_in_sentence)

    def __regex_money(self):
        self.assert_equal('valor de r$400', 'valor de MONEY', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('valor de $400', 'valor de MONEY', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('valor de R$400', 'valor de MONEY', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('valor de rS400', 'valor de MONEY', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('valor de RS400', 'valor de MONEY', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('valor de RS4,00', 'valor de MONEY', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('valor de r$4,00', 'valor de MONEY', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('valor de $4,00', 'valor de MONEY', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('valor de RS40.000', 'valor de MONEY', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('valor de r$400.000,00', 'valor de MONEY', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('valor de r$1.400.000,00', 'valor de MONEY', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('valor de r$10.400.000,00', 'valor de MONEY', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('valor de r$100.400.000,00', 'valor de MONEY', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('valor de r$3478578478949784749784978897478939789', 'valor de MONEY', True, self.tokenizer.replace_words_in_sentence)

    def __regex_url(self):
        self.assert_equal('site https://www.tks.com.br', 'site URL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('site http://www.tks.com.br', 'site URL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('site https://www.tks.com', 'site URL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('site http://www.tks.com', 'site URL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('site www.tks.com', 'site URL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('site www.tks.gov.br', 'site URL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('site www.tks.com.br', 'site URL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('site www.tks.com.br/what-is-titan', 'site URL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('site www.tks.com.br/35544646/what-is-titan', 'site URL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('site www.tks.com.br/35544646/what-is-titan?3345/', 'site URL', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('site https://tks.com.br/35544646/what-is-titan?3345/', 'site URL', True, self.tokenizer.replace_words_in_sentence)

    def __regex_number(self):
        self.assert_equal('é 40', 'é NUMBER', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('é +40', 'é NUMBER', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('é -40', 'é NUMBER', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('é -40.2231', 'é NUMBER', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('é 40.9', 'é NUMBER', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('é 40.1334', 'é NUMBER', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('é 40,343', 'é NUMBER', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('é 40-3455', 'é NUMBER', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('é a 40ª', 'é a NUMBER', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('é o 40º', 'é o NUMBER', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('é 4359488745878477868768764939786879490', 'é NUMBER', True, self.tokenizer.replace_words_in_sentence)

    def __regex_emoji(self):
        self.assert_equal('\U0001f600 era um emoji', ' era um emoji', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('\U0001f64f era um emoji', ' era um emoji', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('\U0001f300 era um emoji', ' era um emoji', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('\U0001f5ff era um emoji', ' era um emoji', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('\U0001f680 era um emoji', ' era um emoji', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('\U0001f6ff era um emoji', ' era um emoji', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('\U0001f1e0 era um emoji', ' era um emoji', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('\U0001f1ff era um emoji', ' era um emoji', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('\U0001f601 era um emoji', ' era um emoji', True, self.tokenizer.replace_words_in_sentence)
        self.assert_equal('\U0001f601\U0001f1ff eram dois emojis', ' eram dois emojis', True, self.tokenizer.replace_words_in_sentence)

    def test_replace_words_with_dicts(self):
        self.assert_equal('vc ta bem?', 'você está bem?', True, self.tokenizer.replace_words_with_dicts)
        self.assert_equal('to ñ', 'estou não', True, self.tokenizer.replace_words_with_dicts)
        self.assert_equal('q blz ond fazer o pagamento', 'que beleza onde fazer o pagamento', True, self.tokenizer.replace_words_with_dicts)
        self.assert_equal('de vdd qdo irá chegar?', 'de verdade quando irá chegar?', True, self.tokenizer.replace_words_with_dicts)
        self.assert_equal('o n° na cc é esse', 'o número na conta corrente é esse', True, self.tokenizer.replace_words_with_dicts)
        self.assert_equal('coracao , atencao e prestacao rimam', 'coração , atenção e prestação rimam', True, self.tokenizer.replace_words_with_dicts)
        self.assert_equal('ate e fe também rimam', 'até e fé também rimam', True, self.tokenizer.replace_words_with_dicts)

    def test_remove_whatsapp_emoji(self):
        self.assert_equal('\U0001f914 \U0001f648 olha quanto emoji nesse \U0001f60c teste aqui', 'olha quanto emoji nesse teste aqui', True, self.tokenizer.remove_whatsapp_emoji)
        self.assert_equal('\U0001f495 \U0001f46d olha quanto emoji nesse \U0001f459 teste aqui', 'olha quanto emoji nesse teste aqui', True, self.tokenizer.remove_whatsapp_emoji)
  
    def test_lowercase_after_punctuation(self):
        self.assert_equal('é mesmo ? Então deu certo ?', 'é mesmo ? então deu certo ?', True, self.tokenizer.lowercase_after_punctuation)
        self.assert_equal('é mesmo ! Então deu certo ?', 'é mesmo ! então deu certo ?', True, self.tokenizer.lowercase_after_punctuation)
        self.assert_equal('é mesmo . Então deu certo ?', 'é mesmo . então deu certo ?', True, self.tokenizer.lowercase_after_punctuation)

    def test_replace_symbol(self):
        self.assert_equal('Sendo assim; não é problema', 'Sendo assim, não é problema', False, self.tokenizer.replace_symbol)
        self.assert_equal('è mesmo? mas e aì? não foi de propòsito', 'é mesmo? mas e aí? não foi de propósito', False, self.tokenizer.replace_symbol)
        self.assert_equal('tá tranqüïlo', 'tá tranquilo', False, self.tokenizer.replace_symbol)
        self.assert_equal('sou de Jaù', 'sou de Jaú', False, self.tokenizer.replace_symbol)

    def test_split_punctuation(self):
        self.assert_equal('tentei, mas não deu', 'tentei , mas não deu', False, self.tokenizer.split_punctuation)
        self.assert_equal('como assim ???', 'como assim ? ? ?', False, self.tokenizer.split_punctuation)
        self.assert_equal('como assim???', 'como assim ? ? ?', False, self.tokenizer.split_punctuation)
        self.assert_equal('como assim  ???', 'como assim ? ? ?', False, self.tokenizer.split_punctuation)
        self.assert_equal('como assim ? ? ?', 'como assim ? ? ?', False, self.tokenizer.split_punctuation)
        self.assert_equal('deu certo!', 'deu certo !', False, self.tokenizer.split_punctuation)
        self.assert_equal('deu certo ?!', 'deu certo ? !', False, self.tokenizer.split_punctuation)
        self.assert_equal('deu certo?!', 'deu certo ? !', False, self.tokenizer.split_punctuation)
        self.assert_equal('esperando...', 'esperando . . .', False, self.tokenizer.split_punctuation)
        self.assert_equal('esperando ...', 'esperando . . .', False, self.tokenizer.split_punctuation)
        self.assert_equal('esperando . ..', 'esperando . . .', False, self.tokenizer.split_punctuation)
        self.assert_equal('esperando .........................................', 'esperando . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .', False, self.tokenizer.split_punctuation)

    def test_remove_symbols(self):
        self.__remove_not_keeping_registry()
        self.__remove_keeping_registry()

    def __remove_not_keeping_registry(self):
        self.assert_equal('como assim > < : ( )???', 'como assim ???', False, self.tokenizer.remove_symbols_not_keeping_registry)
        self.assert_equal('como assim ???> < : ( )', 'como assim ???', False, self.tokenizer.remove_symbols_not_keeping_registry)
        self.assert_equal('#como assim ???', 'como assim ???', False, self.tokenizer.remove_symbols_not_keeping_registry)
        self.assert_equal('como assim $@???', 'como assim ???', False, self.tokenizer.remove_symbols_not_keeping_registry)
        self.assert_equal('´^`~\como assim ???', 'como assim ???', False, self.tokenizer.remove_symbols_not_keeping_registry)
        self.assert_equal('cϕoϕmo aϕsϕsϕiϕmϕ ?ϕ??', 'como assim ???', False, self.tokenizer.remove_symbols_not_keeping_registry)
        self.assert_equal('"como assim ???"', 'como assim ???', False, self.tokenizer.remove_symbols_not_keeping_registry)
        self.assert_equal("'como assim ???'", 'como assim ???', False, self.tokenizer.remove_symbols_not_keeping_registry)

    def __remove_keeping_registry(self):
        self.__check_removal_registry_lst('como assim > < : ( )???', 'como assim ???', False)
        self.__check_removal_registry_lst('como assim ???><:()', 'como assim ???', False)
        self.__check_removal_registry_lst('#como assim ???', 'como assim ???', False)
        self.__check_removal_registry_lst('como assim $@???', 'como assim ???', False)
        self.__check_removal_registry_lst('cϕoϕmo aϕsϕsϕiϕmϕ #*?ϕ??', 'como assim ???', False)
        self.__check_removal_registry_lst('´^`~\como assim ???', 'como assim ???', False)
        self.__check_removal_registry_lst('cϕoϕmo aϕsϕsϕiϕmϕ ?ϕ??', 'como assim ???', False)
        self.__check_removal_registry_lst('"como assim ???"', 'como assim ???', False)
        self.__check_removal_registry_lst("'como assim ???'", 'como assim ???', False)
        self.__check_removal_registry_lst("como assim ???", 'como assim ???', True)

    def __check_removal_registry_lst(self, sentence: str, processed_sentence: str, expected_empty: bool):
        tokenizer_with_registry = SentenceTokenizer(keep_registry_punctuation = True)
        self.assert_equal(sentence, processed_sentence, False, tokenizer_with_registry.remove_symbols_keeping_registry)
        removal_registry_lst = tokenizer_with_registry.removal_registry_lst
        if expected_empty: 
            assert len(removal_registry_lst) == 0, 'Removal Registry List is not empty as expected'
        else:
            assert removal_registry_lst[0][0] == sentence, 'Message "{}" is different from the expected "{}"!'.format(removal_registry_lst[0][0], sentence)
            reconstructed_sentence = self.__get_reconstructed_sentence(processed_sentence, removal_registry_lst[0])
            expected_sentence = ' '.join(sentence.split())
            assert reconstructed_sentence == expected_sentence, 'Incorrect removal_registry_lst "{}" "{}"!'.format(reconstructed_sentence, sentence)

    def __get_reconstructed_sentence(self, processed_sentence: str, removal_registry_lst: list):
        reconstructed_sentence_lst = list(processed_sentence)
        removal_dicts = removal_registry_lst[1:]
        for removed_punctuation in removal_dicts:
            reconstructed_sentence_lst.insert(removed_punctuation['position'], removed_punctuation['punctuation'])
        reconstructed_sentence = ''.join(reconstructed_sentence_lst)
        return reconstructed_sentence

    def test_pre_process(self):
        message = 'Olá, estou precisando do meu boleto com urgência!! Me mande no meu e-mail teste@gmail.com. Também nao estou conseguindo entrar em contato pelo (31)96549-3040'
        expected_message = 'olá , estou precisando do meu boleto com urgência ! ! me mande no meu email EMAIL . também não estou conseguindo entrar em contato pelo PHONE'
        self.assert_equal(message = message, expected_message = expected_message, use_split = False, sentence_tokenizer_function = self.tokenizer.process_message)
        message = 'P/ saber disso eh c/ vc ou consigo ver pelo site www.dúvidas.com.br/minha-dúvida ??'
        expected_message = 'para saber disso é com você ou consigo ver pelo site URL ? ?'
        self.assert_equal(message = message, expected_message = expected_message, use_split = False, sentence_tokenizer_function = self.tokenizer.process_message)

if __name__ == '__main__':
    unittest.main()