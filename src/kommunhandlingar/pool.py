"""Krav: K8, K9 och K12 i docs/02-KRAV.md, ADR-0004. Test: tests/test_hamta.py.

Poolen är tillståndet: front matter i varje `.md` under `data/<kommun>/`,
uppslagen på källnyckel, tidigare källnycklar och sökväg.
"""

from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from kommunhandlingar import frontmatter


@dataclass
class Pool:
    efter_sokvag: dict[PurePosixPath, dict[str, str]] = field(default_factory=dict)
    efter_nyckel: dict[str, PurePosixPath] = field(default_factory=dict)
    tidigare: set[str] = field(default_factory=set)

    def satt(self, sokvag: PurePosixPath, falt: dict[str, str]) -> None:
        if sokvag in self.efter_sokvag:
            self.efter_nyckel.pop(self.efter_sokvag[sokvag]["kallnyckel"], None)
        self.efter_sokvag[sokvag] = falt
        self.efter_nyckel[falt["kallnyckel"]] = sokvag
        self.tidigare.update(frontmatter.lista(falt["tidigare_kallnycklar"]))


def las(data: Path, kommun: str) -> Pool:
    pool = Pool()
    for fil in sorted((data / kommun).rglob("*.md")):
        falt = frontmatter.las(fil.read_text(encoding="utf-8"))
        pool.satt(PurePosixPath(fil.relative_to(data).as_posix()), falt)
    return pool
