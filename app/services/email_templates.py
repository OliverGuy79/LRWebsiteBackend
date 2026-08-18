"""Branded HTML templates for transactional ELR notifications."""

from html import escape


def _value(value: object, fallback: str = "—") -> str:
    text = str(value or "").strip()
    return escape(text) if text else fallback


def _layout(*, eyebrow: str, title: str, intro: str, rows: list[tuple[str, str]], accent: str) -> str:
    table_rows = "".join(
        f"""
        <tr>
          <td style="padding:12px 0;border-bottom:1px solid #ece9e2;color:#777;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;width:145px;vertical-align:top">{escape(label)}</td>
          <td style="padding:12px 0;border-bottom:1px solid #ece9e2;color:#111;font-size:15px;line-height:1.55;vertical-align:top">{value}</td>
        </tr>"""
        for label, value in rows
    )
    return f"""<!doctype html>
<html lang="fr">
  <body style="margin:0;background:#f2efe8;font-family:Arial,Helvetica,sans-serif;color:#111">
    <div style="display:none;max-height:0;overflow:hidden">{escape(intro)}</div>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f2efe8;padding:32px 12px">
      <tr><td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:640px;background:#fff;border-radius:24px;overflow:hidden;border:1px solid #e5e1d8">
          <tr><td style="background:#0b0b0f;padding:34px 38px;color:#fff">
            <div style="font-size:11px;font-weight:800;letter-spacing:.2em;text-transform:uppercase;color:{accent}">{escape(eyebrow)}</div>
            <h1 style="margin:12px 0 0;font-size:30px;line-height:1.1">{escape(title)}</h1>
            <p style="margin:14px 0 0;color:#bbb;font-size:15px;line-height:1.55">{escape(intro)}</p>
          </td></tr>
          <tr><td style="padding:26px 38px 34px">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0">{table_rows}</table>
          </td></tr>
          <tr><td style="padding:20px 38px;background:#f7f5f0;color:#777;font-size:12px;line-height:1.5">
            Notification automatique envoyée depuis le site de l’Église La Rencontre.
          </td></tr>
        </table>
      </td></tr>
    </table>
  </body>
</html>"""


def build_contact_email(data: dict, subject_label: str) -> str:
    message = _value(data.get("message")).replace("\n", "<br>")
    email = _value(data.get("email"))
    phone = _value(data.get("phone"))
    return _layout(
        eyebrow="Nouvelle prise de contact",
        title=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
        intro="Une nouvelle demande vient d’être envoyée depuis le formulaire de contact.",
        accent="#a3ff12",
        rows=[
            ("Prénom", _value(data.get("first_name"))),
            ("Nom", _value(data.get("last_name"))),
            ("Email", f'<a href="mailto:{email}" style="color:#c62035">{email}</a>'),
            ("Téléphone", f'<a href="tel:{phone}" style="color:#c62035">{phone}</a>'),
            ("Sujet", _value(subject_label)),
            ("Message", message),
        ],
    )


def build_reservation_email(data: dict) -> str:
    product = data.get("product") or {}
    phone = _value(data.get("phone"))
    return _layout(
        eyebrow="Nouvelle réservation boutique",
        title=str(product.get("name") or "Article réservé"),
        intro="Une nouvelle demande de réservation attend d’être confirmée avec la personne.",
        accent="#a3ff12",
        rows=[
            ("Client", f"{_value(data.get('firstname'))} {_value(data.get('name'))}"),
            ("Téléphone", f'<a href="tel:{phone}" style="color:#c62035">{phone}</a>'),
            ("Produit", _value(product.get("name"))),
            ("Catégorie", _value(product.get("category"))),
            ("Taille", _value(data.get("size"))),
            ("Couleur", _value(data.get("color"))),
            ("Quantité", _value(data.get("quantity"), "1")),
        ],
    )
