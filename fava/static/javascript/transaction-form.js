import Awesomplete from 'awesomplete';
import fuzzy from 'fuzzyjs';

import { $, $$, handleJSON } from './helpers';
import e from './events';

function submitTransactionForm(successCallback) {
  const jsonData = {
    date: $('#transaction-form input[name=date]').value,
    flag: $('#transaction-form input[name=flag]').value,
    payee: $('#transaction-form input[name=payee]').value,
    narration: $('#transaction-form input[name=narration]').value,
    postings: [],
  };

  $$('.posting:not(.template)').forEach((posting) => {
    const account = posting.querySelector('input[name=account]').value;
    const number = posting.querySelector('input[name=number]').value;
    const currency = posting.querySelector('input[name=currency]').value;

    if (account) {
      jsonData.postings.push({
        account,
        number,
        currency: number ? currency : '',
      });
    }
  });

  const form = $('#transaction-form');
  $.fetch(form.getAttribute('action'), {
    method: 'PUT',
    body: JSON.stringify(jsonData),
    headers: { 'Content-Type': 'application/json' },
  })
    .then(handleJSON)
    .then((data) => {
      form.reset();
      $$('#transaction-form .posting:not(.template)').forEach((el, index) => {
        if (index > 1) {
          el.remove();
        }
      });
      e.trigger('reload');
      e.trigger('info', data.message);
      if (successCallback) {
        successCallback();
      }
    }, (error) => {
      e.trigger('error', `Adding transcation failed: ${error}`);
    });
}

function initInput(input) {
  if (!input.getAttribute('list')) {
    return;
  }

  const options = {
    autoFirst: true,
    minChars: 0,
    maxItems: 30,
    filter(suggestion, search) {
      return fuzzy.test(search, suggestion.value);
    },
  };
  const completer = new Awesomplete(input, options);

  input.addEventListener('focus', () => {
    completer.evaluate();
  });
}

export default function initTransactionForm() {
  $$('#transaction-form .fieldset:not(.template) input').forEach((input) => {
    initInput(input);
  });

  $('#transaction-form-submit').addEventListener('click', (event) => {
    event.preventDefault();
    submitTransactionForm(() => {
      $('.transaction-form').classList.remove('shown');
    });
  });

  $('#transaction-form-submit-and-new').addEventListener('click', (event) => {
    event.preventDefault();
    submitTransactionForm();
  });

  $.delegate($('#transaction-form'), 'click', '.add-posting', (event) => {
    event.preventDefault();
    const newPosting = $('#transaction-form .posting.template').cloneNode(true);
    newPosting.querySelectorAll('input').forEach((input) => {
      input.value = ''; // eslint-disable-line no-param-reassign
      initInput(input);
    });
    $('#transaction-form .postings').appendChild(newPosting);
    newPosting.classList.remove('template');
    newPosting.querySelector('.account').focus();
  });
}
