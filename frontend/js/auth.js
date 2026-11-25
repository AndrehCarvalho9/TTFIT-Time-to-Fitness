(() => {
  const API = 'http://127.0.0.1:8000';
  const $ = (id) => document.getElementById(id);

  async function api(path, options = {}) {
    let response;
    try {
      response = await fetch(API + path, {
        ...options,
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      });
    } catch {
      throw new Error('Não foi possível conectar à API do TTFIT. Feche esta página e inicie o app pelo arquivo iniciar_ttfit.py.');
    }
    if (!response.ok) {
      let data = {};
      try { data = await response.json(); } catch {}
      throw new Error(data.detail || 'Não foi possível concluir a operação.');
    }
    if (response.status === 204) return null;
    return response.json();
  }

  function setStatus(element, message, isError = false) {
    if (!element) return;
    element.textContent = message;
    element.classList.toggle('error', isError);
  }

  async function updateHeader() {
    const link = $('auth-link');
    if (!link) return;
    try {
      await api('/api/auth/me');
      link.textContent = 'Perfil';
      link.href = 'perfil.html';
    } catch {
      link.textContent = 'Entrar';
      link.href = 'login.html';
    }
  }

  function initTabs() {
    const loginTab = $('tab-login');
    const registerTab = $('tab-register');
    if (!loginTab || !registerTab) return;
    const tabs = [loginTab, registerTab];
    const panels = [$('panel-login'), $('panel-register')];
    function select(index) {
      tabs.forEach((tab, i) => {
        tab.classList.toggle('active', i === index);
        tab.setAttribute('aria-selected', String(i === index));
      });
      panels.forEach((panel, i) => { panel.hidden = i !== index; });
    }
    loginTab.addEventListener('click', () => select(0));
    registerTab.addEventListener('click', () => select(1));
  }

  function initLogin() {
    const loginForm = $('login-form');
    const registerForm = $('register-form');

    loginForm?.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!loginForm.reportValidity()) return;
      const button = loginForm.querySelector('button[type="submit"]');
      setStatus($('login-status'), 'Entrando...');
      button.disabled = true;
      try {
        const data = new FormData(loginForm);
        await api('/api/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email: data.get('email'), password: data.get('password') }),
        });
        window.location.href = 'perfil.html';
      } catch (error) {
        setStatus($('login-status'), error.message, true);
      } finally {
        button.disabled = false;
      }
    });

    registerForm?.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!registerForm.reportValidity()) return;
      const data = new FormData(registerForm);
      if (data.get('password') !== data.get('confirm')) {
        setStatus($('register-status'), 'As senhas não coincidem.', true);
        return;
      }
      const button = registerForm.querySelector('button[type="submit"]');
      setStatus($('register-status'), 'Criando conta...');
      button.disabled = true;
      try {
        await api('/api/auth/register', {
          method: 'POST',
          body: JSON.stringify({
            name: data.get('name'),
            email: data.get('email'),
            password: data.get('password'),
          }),
        });
        window.location.href = 'perfil.html';
      } catch (error) {
        setStatus($('register-status'), error.message, true);
      } finally {
        button.disabled = false;
      }
    });
  }

  function showProfile(user) {
    $('profile-name').textContent = user.name;
    $('profile-email').textContent = user.email;
    $('profile-initial').textContent = user.name.trim().charAt(0).toUpperCase() || 'T';
    $('profile-name-input').value = user.name || '';
    $('profile-email-input').value = user.email || '';
    $('profile-age-input').value = user.age ?? '';
    $('profile-height-input').value = user.height_cm ?? '';
    $('profile-weight-input').value = user.weight_kg ?? '';
    $('profile-goal-input').value = user.goal || '';
    $('summary-age').textContent = user.age ? `${user.age} anos` : 'Não informado';
    $('summary-height').textContent = user.height_cm ? `${user.height_cm} cm` : 'Não informada';
    $('summary-weight').textContent = user.weight_kg ? `${user.weight_kg} kg` : 'Não informado';
    $('summary-goal').textContent = user.goal || 'Não informado';
    $('summary-created').textContent = user.created_at
      ? new Date(user.created_at).toLocaleDateString('pt-BR')
      : '—';
  }

  async function initProfile() {
    const form = $('profile-form');
    if (!form) return;
    try {
      const data = await api('/api/auth/me');
      showProfile(data.user);
    } catch {
      window.location.replace('login.html');
      return;
    }

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const button = form.querySelector('button[type="submit"]');
      const payload = {
        name: $('profile-name-input').value.trim(),
        age: $('profile-age-input').value ? Number($('profile-age-input').value) : null,
        height_cm: $('profile-height-input').value ? Number($('profile-height-input').value) : null,
        weight_kg: $('profile-weight-input').value ? Number($('profile-weight-input').value) : null,
        goal: $('profile-goal-input').value.trim(),
      };
      setStatus($('profile-status'), 'Salvando...');
      button.disabled = true;
      try {
        const data = await api('/api/auth/me', { method: 'PUT', body: JSON.stringify(payload) });
        showProfile(data.user);
        setStatus($('profile-status'), 'Perfil atualizado.');
      } catch (error) {
        setStatus($('profile-status'), error.message, true);
      } finally {
        button.disabled = false;
      }
    });

    $('logout-button')?.addEventListener('click', async () => {
      try { await api('/api/auth/logout', { method: 'POST' }); } catch {}
      window.location.href = 'index.html';
    });

    $('delete-account-button')?.addEventListener('click', async () => {
      if (!window.confirm('Excluir sua conta e os dados do perfil? Esta ação não pode ser desfeita.')) return;
      const button = $('delete-account-button');
      button.disabled = true;
      try {
        await api('/api/auth/me', { method: 'DELETE' });
        window.location.href = 'index.html';
      } catch (error) {
        setStatus($('profile-status'), error.message, true);
        button.disabled = false;
      }
    });
  }

  updateHeader();
  initTabs();
  initLogin();
  initProfile();
})();
