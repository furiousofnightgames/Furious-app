# Motor de Temas & UI Premium 🎨✨

O Furious App não é apenas funcional, ele é uma experiência visual. Implementamos um **Dynamic Theme Engine** que adapta a interface para criar imersão total.

## 🌈 Temas Dinâmicos

O sistema permite que o usuário altere a identidade visual do app em tempo real, afetando cores de destaque, gradientes, sombras e efeitos de vidro.

### Presets Cyberpunk
- **Neon Cyan (Padrão)**: A estética clássica cyberpunk, com azuis elétricos e roxos profundos.
- **Toxic Green**: Um tema hacker/matrix focado em verdes e pretos.
- **Hot Pink**: Contraste alto com tons de magenta para máxima vibração.

### Arquitetura CSS (Tailwind)
Utilizamos variáveis CSS nativas (`--color-primary`, `--bg-glass`) manipuladas via JavaScript, permitindo trocas instantâneas sem reload. O uso de `backdrop-filter: blur()` cria a estética **Glassmorphism** moderna que define modais e cards.

---

# Design de Componentes

## 🪟 Modais Glassmorphic
Abandonamos os modais opacos tradicionais. Nossos modais usam desfoque de fundo e bordas translúcidas para manter o contexto da biblioteca visível enquanto foca a atenção na ação.

## 🃏 Cards Holofiol
Os cards de jogos utilizam efeitos de hover tridimensionais e brilhos dinâmicos ("Holo-foil") que reagem ao mouse, simulando cartas colecionáveis raras.

## 📱 Responsividade Fluida
Toda a UI é construída com um grid flexível que se adapta de monitores 4K ultra-wide até janelas compactas estilo "sidebar", garantindo que a biblioteca esteja sempre organizada.
