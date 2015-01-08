# -*- coding: utf-8 -*-
import unittest
import lxml.doctestcompare
import lxml.etree
import doctest

from corpustools import converter


tests = {
    'a-within-li': {
       'html': (
            '<html>'
            '  <body>'
            '    <ul>'
            '      <li>'
            '        <a>Geahčá</a>'
            '      </li>'
            '      <li>'
            '        <a>Geahčá</a>'
            '      </li>'
            '    </ul>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <list>'
            '      <p type="listitem">'
            '               Geahčá'
            '      </p>'
            '      <p type="listitem">'
            '               Geahčá'
            '      </p>'
            '    </list>'
            '  </body>'
            '</document>'
           ),
        },
    'address': {
       'html': (
            '<html>'
            '  <body>'
            '    <address>'
            '      Sametingets plenumsmøte er <a>direktesendt</a>'
            '        .<br />'
            '        Program for fredag 29. mai 08.30-12.30 (pause'
            '        10.30-11.00<br />'
            '       Arbeids- og inkluderingsminister'
            '       til Sametinget<br />'
            '       Sak 25/09 Revidering av Sametingets arbeidsorden<br />'
            '       Sak 26/09 Reinbeitekonvensjonen Norge - Sverige<br />'
            '  </address>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p>'
            '      Sametingets plenumsmøte er direktesendt'
            '      .'
            '      Program for fredag 29. mai 08.30-12.30 (pause'
            '      10.30-11.00'
            '      Arbeids- og inkluderingsminister'
            '      til Sametinget'
            '      Sak 25/09 Revidering av Sametingets arbeidsorden'
            '      Sak 26/09 Reinbeitekonvensjonen Norge - Sverige'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'blockquote-p-and-text': {
       'html': (
            '<html>'
            '  <body>'
            '  <blockquote>'
            '      <p>«at like rettigheter ikke nødvendigvis trenger'
            '  </blockquote>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <span type="quote">'
            '               «at like rettigheter ikke nødvendigvis trenger'
            '      </span>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'blockquote': {
       'html': (
            '<html>'
            '  <body>'
            '  <blockquote>'
            '      <p>Rievdaduvvon.</p>'
            '  </blockquote>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <span type="quote">'
            '               Rievdaduvvon.'
            '      </span>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-a-h2': {
       'html': (
            '<html>'
            '  <body>'
            '    <div>'
            '            <a>'
            '                <h2>'
            '                    Pressesenter'
            '                </h2>'
            '            </a>'
            '    </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p type="title">'
            '            Pressesenter'
            '    </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-a-p': {
       'html': (
            '<html>'
            '  <body>'
            '    <div>'
            '            <a>'
            '                <p>'
            '                    Pressesenter'
            '                </p>'
            '            </a>'
            '    </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      Pressesenter'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-b-and-text': {
       'html': (
            '<html>'
            '  <body>'
            '  <div>'
            '      <b>'
            '               Ohcanáigemearri:'
            '      </b>'
            '      <br />'
            '           15.09.2006.'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="bold">'
            '               Ohcanáigemearri:'
            '      </em>'
            '  </p>'
            '  <p>'
            '           15.09.2006.'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-div-a-span': {
       'html': (
            '<html>'
            '  <body>'
            '  <div>'
            '      <div>'
            '    <a>'
            '          <span>John-Marcus Kuhmunen</span>'
            '    </a>'
            '      </div>'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           John-Marcus Kuhmunen'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-div-a': {
       'html': (
            '<html>'
            '  <body>'
            '  <div>'
            '      <div>'
            '    <a>Geahča buot áššebáhpáriid</a>'
            '    <div style="clear: both"></div>'
            '      </div>'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>Geahča buot áššebáhpáriid</p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-font-and-i': {
       'html': (
            '<html>'
            '  <body>'
            '  <div>'
            '      <font face="Times New Roman">'
            '    <span>'
            '          <font>'
            '                       maajjen'
            '          </font>'
            '    </span>'
            '      </font>'
            '      <i>'
            '    <font face="Times New Roman">'
            '          <span>'
            '            <font>'
            '                           listeforslag,'
            '            </font>'
            '          </span>'
            '    </font>'
            '      </i>'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           maajjen'
            '  </p>'
            '  <p>'
            '      <em type="italic">'
            '               listeforslag,'
            '      </em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-h1-and-a': {
       'html': (
            '<html>'
            '  <body>'
            '  <div>'
            '      <h1>Terje Riis-Johansen</h1>'
            '      <a>'
            '               Taler og artikler'
            '      </a>'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p type="title">'
            '            Terje Riis-Johansen'
            '    </p>'
            '  <p>'
            '           Taler og artikler'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-h1-and-text': {
       'html': (
            '<html>'
            '  <body>'
            '  <div>'
            '      <h1>Ledige stillingar</h1>'
            '           No kan du søke jobb.<br />'
            '           &#160;<br />'
            '           Sjekk også våre rekrutteringssider'
            '      <a title="Jobb i AD">'
            '               Jobb i AD'
            '      </a>'
            '      <br />'
            '      <br />'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p type="title">'
            '            Ledige stillingar'
            '    </p>'
            '  <p>'
            '           No kan du søke jobb.'
            '  </p>'
            '  <p>'
            '  </p>'
            '  <p>'
            '           Sjekk også våre rekrutteringssider'
            '  </p>'
            '  <p>'
            '           Jobb i AD'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-hx': {
       'html': (
            '<html>'
            '  <body>'
            '  <div class='
            '       "artikkel artikkelmal_2">'
            '      <h1>Sámedikki doarjja</h1>'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p type="title">Sámedikki doarjja</p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-p-and-font': {
       'html': (
            '<html>'
            '  <body>'
            '  <div>'
            '      <p>Rikspolitiske verv</p>'
            '      <font face="Times New Roman">abc</font>'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>Rikspolitiske verv</p>'
            '  <p>abc</p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-p-and-text': {
       'html': (
            '<html>'
            '  <body>'
            '  <div>'
            '      <p>'
            '    <strong>'
            '                    Poastadreassa:'
            '    </strong>'
            '    <br />'
            '               Postboks 8036 Dep'
            '    <br />'
            '               0030 Oslo'
            '    <br />'
            '      </p>'
            '           E-poasta:'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="italic">'
            '               Poastadreassa:'
            '      </em>'
            '           Postboks 8036 Dep'
            '           0030 Oslo'
            '  </p>'
            '  <p>'
            '           E-poasta:'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-span': {
       'html': (
            '<html>'
            '  <body>'
            '    <div>'
            '      <span>'
            '        Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '      </span>'
            '    </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p>'
            '      Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '    </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-small-a': {
       'html': (
            '<html>'
            '  <body>'
            '    <div>'
            '      <small>'
            '        <a>'
            '          Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '        </a>'
            '      </small>'
            '    </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p>'
            '      Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '    </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-em-p-em': {
       'html': (
            '<html>'
            '  <body>'
            '    <div>'
            '      <em>'
            '        <p>'
            '          <em>'
            '            Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '          </em>'
            '        </p>'
            '      </em>'
            '    </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p>'
            '      Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '    </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-a-div': {
       'html': (
            '<html>'
            '  <body>'
            '    <div>'
            '      <a>'
            '        <div>'
            '          Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '        </div>'
            '      </a>'
            '    </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p>'
            '      Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '    </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-table': {
       'html': (
            '<html>'
            '  <body>'
            '  <div>'
            '      <table>'
            '    <tbody>'
            '          <tr>'
            '            <td>'
            '                           abc <a>Nynorsk</a> def'
            '            </td>'
            ''
            '            <td>'
            '                           ghi <a>Sámegiella</a> jkl'
            '            </td>'
            ''
            '            <td>'
            '                           mno <a>Normalvisning</a> pqr'
            '            </td>'
            '          </tr>'
            '    </tbody>'
            '      </table>'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           abc'
            '  </p>'
            '  <p>'
            '           Nynorsk'
            '  </p>'
            '  <p>'
            '           def'
            '  </p>'
            '  <p>'
            '           ghi'
            '  </p>'
            '  <p>'
            '           Sámegiella'
            '  </p>'
            '  <p>'
            '           jkl'
            '  </p>'
            '  <p>'
            '           mno'
            '  </p>'
            '  <p>'
            '           Normalvisning'
            '  </p>'
            '  <p>'
            '           pqr'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-text-and-div': {
       'html': (
            '<html dir="ltr">'
            '  <body>'
            '  <div>'
            '           Tällä viikolla<br />'
            '      <br />'
            '           SPN:n hallitus<br />'
            '      <div></div>'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           Tällä viikolla'
            '  </p>'
            '  <p>'
            '           SPN:n hallitus'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-text-and-span': {
       'html': (
            '<html>'
            '  <body>'
            '  <div>'
            '           Laitan blogini lukijoille'
            '      <br />'
            '      <br />'
            '      <span>'
            '               Voimassa oleva'
            '      </span>'
            '      <br />'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>Laitan blogini lukijoille</p>'
            '  <p>Voimassa oleva</p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-text': {
       'html': (
            '<html>'
            '  <body>'
            '  <div>'
            '           Almmuhan Kuhmunen, John-Marcus. <a>Halloi!</a>'
            '           Maŋumustá rievdaduvvon 26.06.2009'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           Almmuhan Kuhmunen, John-Marcus.'
            '  </p>'
            '  <p>'
            '           Halloi!'
            '  </p>'
            '  <p>'
            '           Maŋumustá rievdaduvvon 26.06.2009'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'div-ul': {
       'html': (
            '<html>'
            '  <body>'
            '  <div>'
            '      <ul>'
            '    <li>'
            '          <div>'
            '                   FoU'
            '          </div>'
            '    </li>'
            ''
            '    <li>'
            '          <div>'
            '                   Investeremiidplánen'
            '          </div>'
            '    </li>'
            '      </ul>'
            '  </div>'
            '  <div>'
            '      <ol>'
            '    <li>'
            '          <div>'
            '                   Teknologiaovdánahttin ja DGT (IKT)'
            '          </div>'
            '    </li>'
            ''
            '    <li>'
            '          <div>'
            '                   Guhkesáiggiplánen'
            '          </div>'
            '    </li>'
            '      </ol>'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <list>'
            '      <p type="listitem">FoU</p>'
            '      <p type="listitem">Investeremiidplánen</p>'
            '  </list>'
            '  <list>'
            '      <p type="listitem">Teknologiaovdánahttin ja DGT (IKT)</p>'
            '      <p type="listitem">Guhkesáiggiplánen</p>'
            '  </list>'
            '  </body>'
            '</document>'
           ),
        },
    'div': {
       'html': (
            '<html>'
            '  <body>'
            '  <div>'
            '      <h1>Sámedikki doarjja</h1>'
            ''
            '      <div>'
            '    <div>'
            '    <p>Sámediggi lea juolludan doarjaga.</p>'
            '    </div>'
            '      </div>'
            ''
            '      <div>'
            '    <div>'
            '          <a>'
            '            <span>John-Marcus Kuhmunen</span>'
            '          </a>'
            '    </div>'
            '      </div>'
            '  </div>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p type="title">Sámedikki doarjja</p>'
            ''
            '  <p>'
            '           Sámediggi lea juolludan doarjaga.'
            '  </p>'
            ''
            '  <p>'
            '           John-Marcus Kuhmunen'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'font-span-font-sub': {
       'html': (
            '<html>'
            '  <body>'
            '  <font face="Times New Roman">'
            '      <span>'
            '    <font>'
            '          <sub>'
            '                       aa'
            '          </sub>'
            '    </font>'
            '      </span>'
            '  </font>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p>'
            '            aa'
            '    </p>'
            '  </body>'
            '</document>'
           ),
        },
    'h1-6': {
       'html': (
            '<html>'
            '  <body>'
            '  <h1>header1</h1>'
            '  <h2>header2</h2>'
            '  <h3>header3</h3>'
            '  <h4>header4</h4>'
            '  <h5>header5</h5>'
            '  <h6>header6</h6>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p type="title">header1</p>'
            '    <p type="title">header2</p>'
            '    <p type="title">header3</p>'
            '    <p type="title">header4</p>'
            '    <p type="title">header5</p>'
            '    <p type="title">header6</p>'
            '  </body>'
            '</document>'
           ),
        },
    'h1-b': {
       'html': (
            '<html>'
            '  <body>'
            '  <h1>'
            '      <b>Phone</b>'
            '  </h1>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p type="title">'
            '            Phone'
            '    </p>'
            '  </body>'
            '</document>'
           ),
        },
    'i-within-note': {
       'html': (
            '<html>'
            '  <body>'
            '    <note>Geahča <i>Sámi skuvlahistorjá 2. -girjjis</i></note>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>Geahča</p>'
            '  <p>'
            '    <em type="italic">Sámi skuvlahistorjá 2. -girjjis</em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'li-a-b-font': {
       'html': (
            '<html>'
            '  <body>'
            '  <li>'
            '      <a>'
            '    <b>'
            '          <font>'
            '       Deltakerloven.'
            '          </font>'
            '    </b>'
            '      </a>'
            '  </li>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p type="listitem">'
            '      <em type="bold">'
            '               Deltakerloven.'
            '      </em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'li-div': {
       'html': (
            '<html>'
            '  <body>'
            '  <ul>'
            '      <li>'
            '    <div>'
            '               FoU'
            '    </div>'
            '      </li>'
            ''
            '      <li>'
            '    <div>'
            '               Investeremiidplánen'
            '    </div>'
            '      </li>'
            ''
            '      <li>'
            '    <div>'
            '               Teknologiaovdánahttin ja DGT (IKT)'
            '    </div>'
            '      </li>'
            ''
            '      <li>'
            '    <div>'
            '               Guhkesáiggiplánen'
            '    </div>'
            '      </li>'
            '  </ul>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <list>'
            '      <p type="listitem">FoU</p>'
            '      <p type="listitem">Investeremiidplánen</p>'
            '      <p type="listitem">Teknologiaovdánahttin ja DGT (IKT)</p>'
            '      <p type="listitem">Guhkesáiggiplánen</p>'
            '  </list>'
            '  </body>'
            '</document>'
           ),
        },
    'nobr': {
       'html': (
            '<html>'
            '  <body>'
            '  <nobr>'
            '                    <a title=\'Aktuelt - Nyheiter - 2009\'>'
            '                            2009'
            '                        </a>'
            '                    </nobr>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>2009</p>'
            '  </body>'
            '</document>'
           ),
        },
    'note-within-p': {
       'html': (
            '<html>'
            '  <body>'
            '    <p>'
            '            <a name="[1]">[1] <note>Vestertana.</note>'
            '                <br />'
            '            </a>'
            '            <a name="[2]">[2] <note>Fra 1918.</note>'
            '                <br />'
            '            </a>'
            '    </p>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p>[1] Vestertana. [2] Fra 1918. </p>'
            '  </body>'
            '</document>'
           ),
        },
    'nrk-wbr': {
       'html': (
            '<html>'
            '  <body>'
            '    <wbr/>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  </body>'
            '</document>'
           ),
        },
    'ol-i-li': {
       'html': (
            '<html>'
            '  <body>'
            '    <ol>'
            '            <i>'
            '                <li> Lærer K. Bruflodt</li>'
            '                <li>"   K. Møgster</li>'
            '                <li>"   A. Jox</li>'
            '            </i>'
            '    </ol>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <list>'
            '            <p type="listitem">Lærer K. Bruflodt </p>'
            '            <p type="listitem">" K. Møgster </p>'
            '            <p type="listitem">" A. Jox </p>'
            '    </list>'
            '  </body>'
            '</document>'
           ),
        },
    'ol-within-ol': {
       'html': (
            '<html>'
            '  <body>'
            '  <ol type="1" start="1">'
            '      <li>1</li>'
            '      <li>2'
            '    <ol>'
            '          <li>2.1</li>'
            '          <li>2.2</li>'
            '          <li>2.3</li>'
            '    </ol>'
            '      </li>'
            '      <li>3</li>'
            '      <li>4</li>'
            '      <li>5</li>'
            '  </ol>'
            '  <ul type="1" start="1">'
            '      <li>1</li>'
            '      <li>2'
            '    <ul>'
            '          <li>2.1</li>'
            '          <li>2.2</li>'
            '          <li>2.3</li>'
            '    </ul>'
            '      </li>'
            '      <li>3</li>'
            '      <li>4</li>'
            '      <li>5</li>'
            '  </ul>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <list>'
            '      <p type="listitem">1</p>'
            '      <p type="listitem">'
            '           2'
            '    <list>'
            '          <p type="listitem">2.1</p>'
            '          <p type="listitem">2.2</p>'
            '          <p type="listitem">2.3</p>'
            '    </list>'
            '      </p>'
            '      <p type="listitem">3</p>'
            '      <p type="listitem">4</p>'
            '      <p type="listitem">5</p>'
            '  </list>'
            '  <list>'
            '      <p type="listitem">1</p>'
            '      <p type="listitem">'
            '           2'
            '    <list>'
            '          <p type="listitem">2.1</p>'
            '          <p type="listitem">2.2</p>'
            '          <p type="listitem">2.3</p>'
            '    </list>'
            '      </p>'
            '      <p type="listitem">3</p>'
            '      <p type="listitem">4</p>'
            '      <p type="listitem">5</p>'
            '  </list>'
            '  </body>'
            '</document>'
           ),
        },
    'p-a-b': {
       'html': (
            '<html>'
            '  <body>'
            '  <p>'
            '      <a name="hov8.noteref1">'
            '    <b>'
            '                   [1]'
            '    </b>'
            '      </a>'
            '  </p>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="bold">'
            '               [1]'
            '      </em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'p-b-span': {
       'html': (
            '<html>'
            '  <body>'
            '  <p>'
            '      <b>'
            '    <span lang="NO-BOK">'
            '                   Sámi oahpponeavvojahki – Sámi máhttolokten'
            '    </span>'
            '      </b>'
            '  </p>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="bold">'
            '               Sámi oahpponeavvojahki – Sámi máhttolokten'
            '      </em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'p-font-font-b-span': {
       'html': (
            '<html>'
            '  <body onload="javascript:Operatest();">'
            '  <p>'
            '      <font size="3">'
            '    <font face="Times New Roman">'
            '          <b>'
            '            <span lang="I-SAMI-NO">'
            '                           Bargit'
            '            </span>'
            '          </b>'
            '          <span lang='
            '                    "I-SAMI-NO"'
            '                    xml:lang="I-SAMI-NO">'
            '                       fertejit dahkat.'
            '          </span>'
            '    </font>'
            '      </font>'
            '  </p>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="bold">Bargit</em> fertejit dahkat.'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'p-span-b': {
       'html': (
            '<html>'
            '  <body>'
            '  <p>'
            '      <span lang="NO-BOK">'
            '    <b>'
            '                   sámi guovddáža viidideapmi stáhtabušehttii'
            '    </b>'
            '      </span>'
            '  </p>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="bold">'
            '               sámi guovddáža viidideapmi stáhtabušehttii'
            '      </em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'p-to-p-listitem': {
       'html': (
            '<html>'
            '  <body>'
            '    <p>• mearridit gielddaid <br />'
            '• sihkkarastit eanaresurssaid <br />'
            '• sihkkarastit sámi kultuvrra <br />'
            '• láhčit  <br />'
            '• láhčit vejolašvuođaid <br />'
            '• ovddidit álbmoga  <br />'
            '• váldit dálkkádaga  <br />'
            '• ovddidit servodatsihkkarvuođa</p>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p type="listitem">mearridit gielddaid </p>'
            '    <p type="listitem">sihkkarastit eanaresurssaid </p>'
            '    <p type="listitem">sihkkarastit sámi kultuvrra </p>'
            '    <p type="listitem">láhčit  </p>'
            '    <p type="listitem">láhčit vejolašvuođaid </p>'
            '    <p type="listitem">ovddidit álbmoga  </p>'
            '    <p type="listitem">váldit dálkkádaga  </p>'
            '    <p type="listitem">ovddidit servodatsihkkarvuođa</p>'
            '  </body>'
            '</document>'
           ),
        },
    'pb': {
       'html': (
            '<html>'
            '  <body>'
            '  <h3><pb>Kapittel</pb></h3>'
            '  <p><pb><b>&#167; 1-1.</b></pb></p>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p type="title">Kapittel</p>'
            '  <p><em type="bold">&#167; 1-1.</em></p>'
            '  </body>'
            '</document>'
           ),
        },
    'span-within-li': {
       'html': (
            '<html>'
            '  <body>'
            '    <ul>'
            '      <li>'
            '        <span>'
            '          <a>'
            '            <span>'
            '              <font>Energiija(EV)</font>'
            '            </span>'
            '          </a>'
            '          <a>'
            '            <font>'
            '              <span>(goallostat)</span>'
            '            </font>'
            '          </a>'
            '        </span>'
            '      </li>'
            '      <li>'
            '        <span>'
            '          <a>'
            '            <font>'
            '              <span>Oljo- ja gássassodat (OG)</span>'
            '              <span>(goallostat)</span>'
            '            </font>'
            '          </a>'
            '    </span>'
            '  </li>'
            '  <li>'
            '    <span>'
            '      <a>'
            '        <span>'
            '          <font>Teknologiija</font>'
            '        </span>'
            '      </a>'
            '      (goallostat)'
            '    </span>'
            '  </li>'
            '  <li>'
            '    <span>'
            '      <a>'
            '        <span>'
            '          <font>Ekonomiija</font>'
            '        </span>'
            '      </a>'
            '      (goallostat)'
            '    </span>'
            '  </li>'
            '   <li>'
            '     <span>'
            '       <a>'
            '         <font>'
            '           <span>Gulahallama</span>'
            '           <span>t (gull.)</span>'
            '         </font>'
            '       </a>'
            '       <a>'
            '     </a>'
            '  </span>'
            '  <span>(goallostat)</span>'
            '      </li>'
            '  </ul>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <list>'
            '  <p type="listitem">Energiija(EV) (goallostat)</p>'
            '  <p type="listitem">Oljo- ja gássassodat (OG) (goallostat)</p>'
            '  <p type="listitem">Teknologiija (goallostat)</p>'
            '  <p type="listitem">Ekonomiija (goallostat)</p>'
            '  <p type="listitem">Gulahallama t (gull.) (goallostat)</p>'
            '  </list>'
            '  </body>'
            '</document>'
           ),
        },
    'span': {
       'html': (
            '<html>'
            '  <body>'
            '  <p>'
            '      <span>'
            '    <a>'
            '          <span>'
            '            <font>Energiija</font>'
            '          </span>'
            '    </a>'
            '    <a>'
            '          <font>'
            '            <span>(goallostat)</span>'
            '          </font>'
            '    </a>'
            '      </span>'
            '  </p>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           Energiija (goallostat)'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'sup': {
       'html': (
            '<html>'
            '  <body>'
            '    <ul>'
            '            <li>km<sup>2</sup></li>'
            '    </ul>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <list>'
            '            <p type="listitem">km 2</p>'
            '    </list>'
            '  </body>'
            '</document>'
           ),
        },
    'td-a-b': {
       'html': (
            '<html>'
            '  <body>'
            '  <td>&#160;'
            '      <a>'
            '    <b>'
            '                   Innholdsfortegnelse'
            '    </b>'
            '      </a>'
            '           &#160;'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="bold">'
            '               Innholdsfortegnelse'
            '      </em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-a-div': {
       'html': (
            '<html>'
            '  <body>'
            '    <td>'
            '            <a>'
            '                <div>'
            '                    Klara'
            '                </div>'
            '            </a>'
            '    </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p>'
            '            Klara'
            '    </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-a-p': {
       'html': (
            '<html>'
            '  <body>'
            '    <table>'
            '            <tr>'
            '                <td>'
            '                    <a>'
            '                        <p>'
            '                            Pressesenter'
            '                        </p>'
            '                    </a>'
            '                </td>'
            '            </tr>'
            '    </table>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      Pressesenter'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-a': {
       'html': (
            '<html>'
            '  <body>'
            '  <td>'
            '      <a>22 24 91 03</a>'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           22 24 91 03'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-b-and-text': {
       'html': (
            '<html>'
            '  <body>'
            '  <td>'
            '      <b>'
            '               Ålkine'
            '      </b>'
            '      <br />'
            '           (Guvvie: Grete Austad)'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="bold">'
            '               Ålkine'
            '      </em>'
            '  </p>'
            '  <p>'
            '           (Guvvie: Grete Austad)'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-b': {
       'html': (
            '<html>'
            '  <body>'
            '  <td>'
            '      <b>'
            '               Albert'
            '      </b>'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="bold">'
            '               Albert'
            '      </em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-div': {
       'html': (
            '<html>'
            '  <body>'
            '  <table>'
            '      <tr>'
            '    <td width="99%">'
            '          <div>'
            '            <a name="dok1"></a>'
            ''
            '            <h1>Láhka</h1>'
            ''
            '            <p>Lága</p>'
            ''
            '            <blockquote>'
            '                           <p>Gč. lága suoidnemánu</p>'
            '            </blockquote>'
            '            <a name="hov0.0.1"></a>'
            '            <a name="hov.ing.0.1"></a>'
            '          </div>'
            '    </td>'
            '      </tr>'
            '  </table>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p></p>'
            '    <p type="title">Láhka</p>'
            '  <p>Lága</p>'
            '  <p>'
            '      <span type="quote">Gč. lága suoidnemánu</span>'
            '  </p>'
            '  <p></p>'
            '  <p></p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-font-span-span-span': {
       'html': (
            '<html>'
            '  <body>'
            '    <td>'
            '      <font size="1">'
            '        <span>'
            '          <span>'
            '            <span>'
            '              Møre og Romsdal Fylkkadiggemiellahttu'
            '            </span>'
            '          </span>'
            '        </span>'
            '      </font>'
            '    </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           Møre og Romsdal Fylkkadiggemiellahttu'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-font-span-strong': {
       'html': (
            '<html>'
            '  <body>'
            '  <td>'
            '      <font face="ADMUI3Lg" size="1">'
            '    <span>'
            '          <strong>Politihkalaš doaimmat</strong>'
            '    </span>'
            '      </font>'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="italic">'
            '        Politihkalaš doaimmat'
            '      </em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-font-span': {
       'html': (
            '<html>'
            '  <body>'
            '    <td>'
            '      <font size="1">'
            '        <span>'
            '          Stáhtačálli, Eanandoallo- ja biebmodepartemeanta'
            '    </span>'
            '      </font>'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           Stáhtačálli, Eanandoallo- ja biebmodepartemeanta'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-font': {
       'html': (
            '<html>'
            '  <body>'
            '  <td>'
            '      <font size="1">Kvirrevitt</font>'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           Kvirrevitt'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-h2-and-text-and-p': {
       'html': (
            '<html>'
            '  <body>'
            '  <td>'
            '      <h2>'
            '               Departementet ber skoledirektøren om hjelp'
            '      </h2>'
            ''
            '           For å kunne '
            ''
            '      <p>'
            '               Kirkedepartementet'
            '      </p>'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p type="title">'
            '            Departementet ber skoledirektøren om hjelp'
            '    </p>'
            ''
            '  <p>'
            '           For å kunne '
            '  </p>'
            ''
            '  <p>'
            '           Kirkedepartementet'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-h3': {
       'html': (
            '<html>'
            '  <body>'
            '  <td width="291">'
            '      <h3 class='
            '           "O-TIT-SEKSJON LEFT">'
            '      <span class='
            '           "O-text"><a'
            '           name="høringsinstanser"></a>'
            '           Gulaskuddanásahusat</span></h3>'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p type="title">'
            '            Gulaskuddanásahusat'
            '    </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-p-and-b': {
       'html': (
            '<html>'
            '  <body>'
            '  <td>'
            '      <p>'
            '    <b>'
            '                   er født i 1937'
            '    </b>'
            '      </p>'
            ''
            '      <b>'
            '               arbeidd innafor mange yrke'
            '      </b>'
            '      <br />'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="bold">'
            '               er født i 1937'
            '      </em>'
            '  </p>'
            ''
            '  <p>'
            '      <em type="bold">'
            '               arbeidd innafor mange yrke'
            '      </em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-p': {
       'html': (
            '<html>'
            '  <body>'
            '  <td width="585">'
            '      <p>'
            '    <span>'
            '          <span>'
            '            <span>'
            '                           link'
            '            </span>'
            '            <span>'
            '                           int'
            '            </span>'
            '            <span>'
            '                           høringsinstanser'
            '            </span>'
            '          </span>'
            '          <span>'
            '                       Gulaskuddanásahusat'
            '          </span>'
            '    </span>'
            '      </p>'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           link'
            '           int'
            '           høringsinstanser'
            '           Gulaskuddanásahusat'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-span-and-b-and-p': {
       'html': (
            '<html>'
            '  <body>'
            '    <table>'
            '      <tr>'
            '        <td>'
            '          <span>'
            '            <font>Riikkačoahkkincealkámušat 2006</font>'
            '          </span>'
            '          <b>NSR 38. Riikkačoahkkin</b>'
            '          <br />'
            '          <br />'
            '          <br />'
            '          <p>'
            '            <span>'
            '                           Norgga Sámiid Riikkasearvvi '
            '            </span>'
            '                       2006'
            '          </p>'
            '        </td>'
            '      </tr>'
            '    </table>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>Riikkačoahkkincealkámušat 2006</p>'
            '  <p>'
            '      <em type="bold">'
            '               NSR 38. Riikkačoahkkin'
            '      </em>'
            '  </p>'
            '  <p>'
            '           Norgga Sámiid Riikkasearvvi  2006'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-span-font': {
       'html': (
            '<html>'
            '  <body>'
            '  <td>'
            '      <span>'
            '    <font size="5">'
            '                   Riikkačoahkkincealkámušat 2006'
            '    </font>'
            '      </span>'
            '      <b>NSR 38.</b>'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           Riikkačoahkkincealkámušat 2006'
            '  </p>'
            '  <p>'
            '      <em type="bold">'
            '               NSR 38.'
            '      </em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-span': {
       'html': (
            '<html>'
            '  <body>'
            '    <td><span>Náitalan, 3 máná</span></td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p>Náitalan, 3 máná</p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-strong': {
       'html': (
            '<html>'
            '  <body>'
            '    <td>'
            '      <strong>Gaskavahkku</strong>'
            '    </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="italic">Gaskavahkku</em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-table-tr-td': {
       'html': (
            '<html>'
            '  <body>'
            '  <td>'
            '      <table>'
            '    <tr>'
            '          <td>Kvirrevitt</td>'
            '    </tr>'
            '      </table>'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           Kvirrevitt'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-text-and-i-and-p': {
       'html': (
            '<html>'
            '  <body>'
            '  <td>'
            '      Nuohta:'
            '      <i>'
            '        Jeg går og rusler på Ringerike'
            '      </i>'
            '      <p>'
            '        Mii læt dal čoagganan manga guovllos'
            '      </p>'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           Nuohta:'
            '  </p>'
            '  <p>'
            '      <em type="italic">'
            '               Jeg går og rusler på Ringerike'
            '      </em>'
            '  </p>'
            '  <p>'
            '           Mii læt dal čoagganan manga guovllos'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'td-u': {
       'html': (
            '<html>'
            '  <body>'
            '  <td>'
            '      <u>Ášši nr. 54/60:</u>'
            '  </td>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="italic">Ášši nr. 54/60:</em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'th-b': {
       'html': (
            '<html>'
            '  <body>'
            '  <th>'
            '      <b>Språktilbudet</b>'
            '  </th>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="bold">Språktilbudet</em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'th-div': {
       'html': (
            '<html>'
            '  <body>'
            '  <th scope="col">'
            '      <div>'
            '               Jan'
            '      </div>'
            '  </th>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           Jan'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'th-p': {
       'html': (
            '<html>'
            '  <body>'
            '  <th>'
            '      <p>Kap. Poasta</p>'
            '  </th>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '           Kap. Poasta'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'thead': {
       'html': (
            '<html>'
            '  <body>'
            '  <thead>'
            '  </thead>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  </body>'
            '</document>'
           ),
        },
    'tr-td-em': {
       'html': (
            '<html>'
            '  <body>'
            '  <tr>'
            '      <td>'
            '    <em>'
            '                   Kapittel 1'
            '    </em>'
            '      </td>'
            '  </tr>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <p>'
            '      <em type="italic">'
            '               Kapittel 1'
            '      </em>'
            '  </p>'
            '  </body>'
            '</document>'
           ),
        },
    'ul-li-div-p': {
       'html': (
            '<html>'
            '  <body>'
            '  <ul>'
            '      <li style='
            '           "list-style: none; display: inline">'
            '    <div>'
            '          <p>'
            '                       Friskt'
            '          </p>'
            '    </div>'
            ''
            '    <div>'
            '          <p>'
            '                       Skogeieren'
            '          </p>'
            '    </div>'
            ''
            '    <div>'
            '          <p>'
            '                       Så langt det'
            '          </p>'
            '    </div>'
            '      </li>'
            '  </ul>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <list>'
            '      <p type="listitem">'
            '               Friskt'
            '      </p>'
            '      <p type="listitem">'
            '               Skogeieren'
            '      </p>'
            '      <p type="listitem">'
            '               Så langt det'
            '      </p>'
            '  </list>'
            '  </body>'
            '</document>'
           ),
        },
    'ul-li-p-i': {
       'html': (
            '<html>'
            '  <body>'
            '  <ul>'
            '      <li>'
            '    <i>'
            '                   4. Slik språkforholdene'
            '    </i>'
            ''
            '    <p>'
            '          <i>'
            '                       Som alle andre'
            '          </i>'
            '    </p>'
            ''
            '    <p>'
            '          <i>'
            '                       Vi erklærer'
            '          </i>'
            '    </p>'
            '      </li>'
            '  </ul>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '  <list>'
            '      <p type="listitem">'
            '    <em>'
            '                   4. Slik språkforholdene'
            '    </em>'
            '    <em>'
            '                   Som alle andre'
            '    </em>'
            '    <em>'
            '                   Vi erklærer'
            '    </em>'
            '      </p>'
            '  </list>'
            '  </body>'
            '</document>'
           ),
        },
    'ul-strong': {
       'html': (
            '<html>'
            '  <body>'
            '    <html:ul>'
            '            <html:strong>'
            '                Pressesenter'
            '            </html:strong>'
            '    </html:li>'
            '  </body>'
            '</html>'
           ),
       'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <list>'
            '            <p>'
            '                Pressesenter'
            '            </p>'
            '    </list>'
            '  </body>'
            '</document>'
           ),
        },
    'div-div-abbr': {
        'html': (
            '<html>'
            '  <body>'
            '    <html:div>'
            '      <html:div>'
            '        <html:abbr>'
            '           Kl.'
            '        </html:abbr>'
            '        11.00'
            '      </html:div>'
            '    </html:div>'
            '  </body>'
            '</html>'
            ),
        'xml': (
            '<document>'
            '  <header>'
            '    <title/>'
            '  </header>'
            '  <body>'
            '    <p>'
            '      Kl.'
            '    </p>'
            '    <p>'
            '      11.00'
            '    </p>'
            '  </body>'
            '</document>'
            ),
        },
    }


def assertXmlEqual(got, want):
    """Check if two xml snippets are equal
    """
    got = lxml.etree.tostring(got)
    want = lxml.etree.tostring(want)
    checker = lxml.doctestcompare.LXMLOutputChecker()
    if not checker.check_output(want, got, 0):
        message = checker.output_difference(
            doctest.Example("", want), got, 0).encode('utf-8')
        raise AssertionError(message)


def test_conversion():
    for testname, html_xml in tests.iteritems():
        yield check_conversion, testname, html_xml


def check_conversion(testname, html_xml):
    '''Check that the tidied html is correctly converted
    to corpus xml via the xhtml2corpus.xsl style sheet
    '''
    got = converter.HTMLContentConverter(
        testname, html_xml['html'],
        None).convert2intermediate()
    want = lxml.etree.fromstring(html_xml['xml'])
    assertXmlEqual(got, want)
