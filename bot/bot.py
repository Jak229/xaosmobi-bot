import re
import requests
from rich import print

from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from .errors import ItemHasMaxQualityLevel


class Bot:
    UA = UserAgent()
    MAIN_L = "http://xaos.mobi/index.php?"

    def __init__(
        self, name: str, password: str, log: bool = True, spaces: bool = False
    ):
        self.name = name
        self.password = password
        self.log = log
        self.spc = spaces

        self.ses = requests.Session()
        self.ses.headers = {"User-Agent": self.UA.random}

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, val: str) -> None:
        if isinstance(val, str):
            if len(val) > 0 and len(val) <= 16:
                self.__name = val
            else:
                raise ValueError(
                    "the lenght name must be less than 16 char and more than 0"
                )
        else:
            raise TypeError(f"name type must be a string, not {type(val).__name__}")

    @property
    def password(self) -> str:
        return self.__password

    @password.setter
    def password(self, val: str) -> None:
        if isinstance(val, str):
            if len(val) >= 3 and len(val) <= 32:
                self.__password = val
            else:
                raise ValueError(
                    "the lenght name must be less than 32 char and more than 3"
                )
        else:
            raise TypeError(f"name type must be a string, not {type(val).__name__}")

    def get_link(self, loc: str) -> str:
        index_p = self.ses.get(self.MAIN_L)

        if loc == "arena":
            link_to_arn = bs(index_p.text, "html.parser").find(
                lambda tag: tag.name == "a" and "Aрeнa Смeрти" in tag.text
            )
            return link_to_arn

        elif loc == "wrk":
            trn_l = bs(index_p.text, "html.parser").find(
                lambda tag: tag.name == "a" and "Тренировочный Лагерь" in tag.text
            )["href"]
            trn_p = self.ses.get(self.MAIN_L + trn_l)
            link_to_wrk = bs(trn_p.text, "html.parser").find(
                lambda tag: tag.name == "a" and "Мастерская" in tag.text
            )["href"]

            return link_to_wrk

    def login(self) -> bool:
        if self.spc is False:
            data = {
                "name": self.name,
                "password": self.password,
                "login": "Войти в игру",
            }
            login = self.ses.post(self.MAIN_L, data=data)
        else:
            headers = {"Cookie": f"userid={self.name}; pass={self.password}; set_i=2"}
            login = self.ses.post(self.MAIN_L, headers=headers)

        if "Aрeнa Смeрти" in login.text:
            return True
        return False

    def get_equipment(self, wrk_link: str) -> list:
        wrk_p = self.ses.get(self.MAIN_L + wrk_link)
        wrk_bs = bs(wrk_p.text, "html.parser")

        items_f = wrk_bs.find_all("div", class_="menu_link3")
        return items_f

    def __log(self, message: str, color: str) -> None:
        if self.log:
            print(f"[bold {color}][{self.name}] {message}")

    def up_quality(self, num_item: int, n: int) -> None:
        wrk_link = self.get_link("wrk")
        items = self.get_equipment(wrk_link)

        qlt_level = re.findall(r"\[(\d+)/(\d+)\]", str(items[int(num_item) - 1]))[0]
        qlt_level_p = int(qlt_level[0])
        qlt_level_t = int(qlt_level[1])

        qlt = items[int(num_item) - 1].findChild(
            lambda tag: tag.name == "a" and "качество" in tag.text
        )

        if qlt is None:
            raise ItemHasMaxQualityLevel

        up_qlt = self.ses.get(self.MAIN_L + qlt["href"])

        up_qlt_bs = bs(up_qlt.text, "html.parser")
        up_for_gold_l = up_qlt_bs.find(
            lambda tag: tag.name == "a" and "Поднять качество за" in tag.text
        )

        for _ in range(int(n)):
            up_for_gold = self.ses.get(self.MAIN_L + up_for_gold_l["href"])

            if "Вы успешно подняли качество предмета." in up_for_gold.text:
                qlt_level_p += 1
                self.__log(
                    "You have successfully raised the quality of the item [%i/%i]"
                    % (qlt_level_p, qlt_level_t),
                    "green",
                )
            else:
                wrk_p = self.ses.get(self.MAIN_L + wrk_link)
                wrk_bs = bs(wrk_p.text, "html.parser")

                items_f = wrk_bs.find_all("div", class_="menu_link3")

                if "эпоха" not in items_f[int(num_item) - 1].text:
                    try:
                        qlt = items_f[int(num_item) - 1].findChild(
                            lambda tag: tag.name == "a" and "качество" in tag.text
                        )
                        up_qlt = self.ses.get(self.MAIN_L + qlt["href"])
                        up_qlt_bs = bs(up_qlt.text, "html.parser")
                        up_for_gold_l = up_qlt_bs.find(
                            lambda tag: tag.name == "a"
                            and "Поднять качество за" in tag.text
                        )
                    except:
                        pass

                if qlt_level_p == qlt_level_t:
                    wrk_bs = bs(up_for_gold.text, "html.parser")
                    items_f = wrk_bs.find_all("div", class_="menu_link3")

                if "эпоха" in items_f[int(num_item) - 1].text:
                    epoxa_link = items_f[int(num_item) - 1].find(
                        lambda tag: tag.name == "a" and "эпоха" in tag.text
                    )
                    epoxa_up_tab = self.ses.get(self.MAIN_L + epoxa_link["href"])
                    epoxa_up_tab_bs = bs(epoxa_up_tab.text, "html.parser")
                    epoxa_up_confirm_l = epoxa_up_tab_bs.find(
                        lambda tag: tag.name == "a"
                        and "Перейти в новую эпоху" in tag.text
                    )

                    self.ses.get(self.MAIN_L + epoxa_up_confirm_l["href"])
                    self.__log("The item has entered a new era!", "blue")
                    qlt_level_p -= 15
                    qlt_level_t += 10
                    continue

                if "трансформировать" in items_f[int(num_item) - 1].text:
                    transform_l = items_f[int(num_item) - 1].find(
                        lambda tag: tag.name == "a" and "трансформировать" in tag.text
                    )
                    transf_up_tab = self.ses.get(self.MAIN_L + transform_l["href"])

                    transform_up_tab = bs(transf_up_tab.text, "html.parser")
                    transform_up_confirm_l = transform_up_tab.find(
                        lambda tag: tag.name == "a" and "Да, продолжить" in tag.text
                    )
                    self.ses.get(self.MAIN_L + transform_up_confirm_l["href"])
                    self.__log("The item is transformed!", "blue")
                    continue

                else:
                    raise ItemHasMaxQualityLevel

    def rec_of_hp(self):
        index_p = self.ses.get(self.MAIN_L)
        link_to_arn = bs(index_p.text, "html.parser").find(
            lambda tag: tag.name == "a" and "Aрeнa Смeрти" in tag.text
        )
        arena = self.ses.get(self.MAIN_L + link_to_arn["href"])

        if "Вы очень слабы" in arena.text:
            jour_div = (
                bs(arena.text, "html.parser")
                .find(
                    lambda tag: tag.name == "div"
                    and tag.get("class")
                    and tag.get("class")[0] == "jour"
                    and "Вы очень слабы" in tag.text
                )
                .find("a")["href"]
            )
            self.ses.get(self.MAIN_L + jour_div)
            self.__log("You have recovered your health!", "yellow")

    def arena(self, n: int = 100) -> None:
        for _ in range(int(n)):
            link_to_arn = self.get_link("arena")
            arena = self.ses.get(self.MAIN_L + link_to_arn["href"])
            arena_bs = bs(arena.text, "html.parser")
            attack_l = arena_bs.find(
                lambda tag: tag.name == "div"
                and tag.get("class")
                and tag.get("class")[0] == "menu_link3"
                and re.findall(r"aтaк\w+", tag.text.lower())
            ).find_all("a")

            start_attack = self.ses.get(
                self.MAIN_L + attack_l[1 if len(attack_l) == 3 else 0]["href"]
            )

            if "Вы очень слабы" in start_attack.text:
                self.rec_of_hp()
                continue

            if "У вас не хватает энергии" in start_attack.text:
                self.energy_recovery()
                continue

            attack_bs = bs(start_attack.text, "html.parser")
            attack_ll = attack_bs.find(
                lambda tag: tag.name == "div"
                and tag.get("class")
                and tag.get("class")[0] == "jour"
                and re.findall(r"бить", tag.text.lower())
            ).find_all("a")

            while True:
                try:
                    attack = self.ses.get(
                        self.MAIN_L + attack_ll[1 if len(attack_ll) == 3 else 0]["href"]
                    )

                    if "Вы очень слабы" in attack.text:
                        self.rec_of_hp()
                        break

                    if "У вас не хватает энергии." in attack.text:
                        self.energy_recovery()
                        break

                    attack_bs = bs(attack.text, "html.parser")
                    attack_ll = attack_bs.find(
                        lambda tag: tag.name == "div"
                        and tag.get("class")
                        and tag.get("class")[0] == "jour"
                        and "Бить прoтивникa" in tag.text
                    ).find_all("a")

                    jour = attack_bs.find("div", class_="jour")
                    result = "".join(
                        [
                            i.text
                            for i in list(jour.children)[
                                : (7 if "Победа" in jour.text else 5)
                            ]
                        ]
                    )
                    color = ""

                    if "Победа" in result:
                        color = "green"
                    elif "Ничья" in result:
                        color = "yellow"
                    else:
                        color = "red"

                    self.__log(result, color)

                except AttributeError:
                    self.energy_recovery()
                    break

    def energy_recovery(self) -> None:
        link_to_arn = self.get_link("arena")
        arena = self.ses.get(self.MAIN_L + link_to_arn["href"])

        if "Вы очень слабы" in arena.text:
            self.rec_of_hp()
            arena = self.ses.get(self.MAIN_L + link_to_arn["href"])

        arena_bs = bs(arena.text, "html.parser")
        attack_l = arena_bs.find(
            lambda tag: tag.name == "div"
            and tag.get("class")
            and tag.get("class")[0] == "menu_link3"
            and re.findall(r"aтaк\w+", tag.text.lower())
        ).find_all("a")

        while True:
            try:
                att = attack_l[1 if len(attack_l) == 2 else 0]

            except Exception as e:
                print(attack_l)
                self.__log(e, "red")

            attack = self.ses.get(self.MAIN_L + att["href"])

            if "Вы очень слабы" in attack.text:
                self.rec_of_hp()
                continue

            if "У вас не хватает энергии." in attack.text:
                arena_bs = bs(attack.text, "html.parser")
                link_r_e = arena_bs.find(
                    lambda tag: tag.name == "div"
                    and tag.get("class")
                    and tag.get("class")[0] == "jour"
                    and "У вас не хватает энергии." in tag.text
                ).find("a")

                self.ses.get(self.MAIN_L + link_r_e["href"])
                self.__log("You have regained energy", "blue")
                break

            arena_bs = bs(attack.text, "html.parser")

            try:
                attack_l = arena_bs.find(
                    lambda tag: tag.name == "div"
                    and tag.get("class")
                    and tag.get("class")[0] == "jour"
                    and re.findall(r"бить", tag.text.lower())
                ).find_all("a")

            except Exception as e:
                pass
