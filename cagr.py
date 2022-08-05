from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from mechanicalsoup import StatefulBrowser

ForumRoomId: TypeAlias = str
StudentId: TypeAlias = str


@dataclass(frozen=True)
class ForumRoom:
    id: ForumRoomId
    name: str


@dataclass
class CAGR:
    browser: StatefulBrowser

    class AuthError(Exception):
        pass

    @staticmethod
    def login(username: str, password: str) -> CAGR:
        browser = StatefulBrowser()
        url = "https://sistemas.ufsc.br/login"
        browser.open(url, params={"service": "http://forum.cagr.ufsc.br/"})

        browser.select_form("#fm1")
        browser["username"] = username
        browser["password"] = password
        response = browser.submit_selected()

        if not response.ok:
            raise CAGR.AuthError()

        return CAGR(browser)

    def list_rooms(self) -> list[ForumRoom]:
        url = "http://forum.cagr.ufsc.br/formularioBusca.jsf"
        self.browser.open(url)

        self.browser.select_form("form#buscaSala")

        params = {
            "buscaSala": "buscaSala",
            "buscaSala:j_id_jsp_632900747_29": "graduandos",
            "buscaSala:j_id_jsp_632900747_34": "Buscar",
            "javax.faces.ViewState": "j_id1",
        }

        for key, value in params.items():
            self.browser[key] = value

        soup = self.browser.submit_selected().soup
        rows = soup.find_all("td", attrs={"class": "coluna1_listar_salas"})

        links = (row.find("a") for row in rows)
        return [
            ForumRoom(
                id=link["href"].split("salaId=")[-1],
                name=link.get_text(strip=True).replace("**Graduandos do Curso: ", ""),
            )
            for link in links
        ]

    def list_student_ids(self, room_id: ForumRoomId) -> list[StudentId]:
        url = "http://forum.cagr.ufsc.br/listarMembros.jsf"

        self.browser.open(url, params={"salaId": room_id})
        page = self.browser.get_current_page()

        cells = page.find_all("td", class_="coluna2_listar_membros")
        return [cell.get_text(strip=True) for cell in cells]
