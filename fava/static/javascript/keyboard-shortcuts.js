import Mousetrap from 'mousetrap';
import 'mousetrap/plugins/bind-dictionary/mousetrap-bind-dictionary';

import { $, $$ } from './helpers';

export function updateKeyboardShortcuts() {
  // Change page
  $$('aside a').forEach((element) => {
    const key = element.getAttribute('data-key');
    if (key !== undefined) {
      Mousetrap.bind(key, () => {
        element.click();
      });
    }
  });

  // Charts
  if ($('#charts')) {
    Mousetrap.bind({
      'ctrl+c': () => {
        $('#toggle-chart').click();
      },
      c() {
        const next = $('#chart-labels .selected').nextElementSibling;

        if (next) {
          next.click();
        } else {
          $('#chart-labels label:first-child').click();
        }
      },
      'shift+c': () => {
        const prev = $('#chart-labels .selected').previousElementSibling;

        if (prev) {
          prev.click();
        } else {
          $('#chart-labels label:last-child').click();
        }
      },
    }, 'keyup');
  }

  // Journal
  if ($('#entry-filters')) {
    Mousetrap.bind({
      p() {
        $('#entry-filters button[data-type=postings]').click();
      },
      m() {
        $('#entry-filters button[data-type=metadata]').click();
      },

      's o': () => {
        $('#entry-filters button[data-type=open]').click();
      },
      's c': () => {
        $('#entry-filters button[data-type=close]').click();
      },
      's t': () => {
        $('#entry-filters button[data-type=transaction]').click();
      },
      's b': () => {
        $('#entry-filters button[data-type=balance]').click();
      },
      's n': () => {
        $('#entry-filters button[data-type=note]').click();
      },
      's d': () => {
        $('#entry-filters button[data-type=document]').click();
      },
      's p': () => {
        $('#entry-filters button[data-type=pad]').click();
      },
      's q': () => {
        $('#entry-filters button[data-type=query]').click();
      },
      's shift+c': () => {
        $('#entry-filters button[data-type=custom]').click();
      },
      's shift+b': () => {
        $('#entry-filters button[data-type=budget]').click();
      },

      't c': () => {
        $('#entry-filters button[data-type=cleared]').click();
      },
      't p': () => {
        $('#entry-filters button[data-type=pending]').click();
      },
      't o': () => {
        $('#entry-filters button[data-type=other]').click();
      },
    }, 'keyup');
  }
}

export function initKeyboardShortcuts() {
  Mousetrap.bind({
    '?': () => {
      $('#keyboard-shortcuts').classList.add('shown');
    },
    esc() {
      $$('.overlay-wrapper').forEach((el) => { el.classList.remove('shown'); });
    },
  }, 'keyup');

  // Filtering:
  Mousetrap.bind({
    'f f': () => {
      $('#from-filter').focus();
    },
    'f t': () => {
      $('#time-filter').focus();
    },
    'f g': () => {
      $('#tag-filter').focus();
    },
    'f a': () => {
      $('#account-filter').focus();
    },
    'f p': () => {
      $('#payee-filter').focus();
    },
  }, 'keyup');
}
