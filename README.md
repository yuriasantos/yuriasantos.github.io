# Yuri Alexandre dos Santos - Personal Page

Landing page pessoal com suporte bilingual (PT-BR / EN-US) e dark/light mode.

## Estrutura

```
index.html          # Pagina principal
robots.txt          # Regras para crawlers
sitemap.xml         # Mapa do site para SEO
assets/
  css/styles.css    # Estilos (design tokens, responsivo, temas)
  js/script.js      # Traducoes, tema, menu mobile, cards expandiveis
  img/
    photo.png       # Foto de perfil
    og-image.png    # Imagem para preview em redes sociais (1200x630)
    favicon.svg     # Favicon vetorial
```

## Deploy no GitHub Pages

1. Crie um repositorio no GitHub (ex: `yuriasantos/yuriasantos.github.io`)
2. Faca push para o branch `main`:

```bash
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

3. Em **Settings > Pages** do repositorio:
   - **Source**: Deploy from a branch
   - **Branch**: main
   - **Folder**: / (root)

4. A pagina ficara disponivel em `https://seu-usuario.github.io/`

## Personalizacao

### Conteudo

- Edite as traducoes em `assets/js/script.js` (objetos `pt` e `en`)
- Publicacoes: edite diretamente no `index.html` (secao `#publications`)
- Links de contato: edite no `index.html` (secao `#contact`)

### Imagens

- **Foto**: substitua `assets/img/photo.png` (proporcao vertical, recomendado 440x560px)
- **OG Image**: substitua `assets/img/og-image.png` (1200x630px)
- **Favicon**: edite `assets/img/favicon.svg`

### SEO

- Atualize a URL canonica e OG tags no `<head>` do `index.html`
- Atualize o JSON-LD (structured data) com seus dados
- Atualize `sitemap.xml` e `robots.txt` com seu dominio final

### Tema

- Dark mode (padrao) e light mode, alternavel pelo toggle na navbar
- Cores definidas como CSS custom properties em `:root` e `[data-theme="light"]` no `styles.css`
- Preferencia do usuario salva em `localStorage`

## Funcionalidades

- Bilingual (PT-BR / EN-US) com persistencia via `localStorage`
- Dark / Light mode toggle
- Cards de atuacao com detalhe expandivel
- Scroll reveal nas secoes
- Navbar fixa com blur ao scrollar
- Menu mobile (hamburger)
- Email ofuscado contra bots
- SEO: Open Graph, JSON-LD, sitemap, robots.txt
- Bloqueio de crawlers de IA no `robots.txt`
- 100% estatico, sem build step
