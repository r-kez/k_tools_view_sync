import bpy

# Translation
translations_dict = {}
# Brazilian Portuguese
try:
    from .locale import pt_br
    translations_dict["pt_BR"] = pt_br.dictionary
except ImportError:
    pass
# Portuguese
try:
    from .locale import pt_pt
    translations_dict["pt_PT"] = pt_pt.dictionary
except ImportError:
    pass
# Ukranian
try:
    from .locale import uk_ua
    translations_dict["uk_UA"] = uk_ua.dictionary
except ImportError:
    pass
# Spanish
try:
    from .locale import es
    translations_dict["es"] = es.dictionary
except ImportError:
    pass
# Japanese
try:
    from .locale import ja_jp
    translations_dict["ja_JP"] = ja_jp.dictionary
except ImportError:
    pass
# Korean
try:
    from .locale import ko_kr
    translations_dict["ko_KR"] = ko_kr.dictionary
except ImportError:
    pass
# Symplified Chinese
try:
    from .locale import zh_hans
    translations_dict["zh_HANS"] = zh_hans.dictionary
except ImportError:
    pass
# Russian
try:
    from .locale import ru_ru
    translations_dict["ru_RU"] = ru_ru.dictionary
except ImportError:
    pass
# French
try:
    from .locale import fr_fr
    translations_dict["fr_FR"] = fr_fr.dictionary
except ImportError:
    pass

