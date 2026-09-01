# Premiere Pro UXP: engineering contract

## Scope

Premiere Pro UXP состоит из двух связанных поверхностей: UXP Core APIs для UI, filesystem, network и системных операций и Premiere DOM APIs для проектов, sequences, tracks, clips и exports. Точка входа Premiere DOM — JavaScript-модуль `require("premierepro")`.

## Manifest and compatibility

Каждый UXP plugin имеет один `manifest.json`. В нём задаются identity plugin, version, host compatibility, entrypoints и permissions. Premiere поддерживает manifest version `5`; официальные материалы указывают `host.minVersion` как границу совместимости.

Комбинация `host.minVersion`, версии `@adobe/premierepro` и фактической версии Premiere должна тестироваться как единый compatibility tuple. API, появившийся в более новой версии UXP/DOM, при запуске на старом host может привести к runtime failure, даже если JavaScript синтаксически корректен.

## Entrypoints and lifecycle

В текущем публичном контракте entrypoints включают panels и commands. Plugin-level hooks — `create()` и `destroy()`; panel-level hooks — `create()`, `show()`, `hide()` и `destroy()`.

Adobe отдельно отмечает, что в Premiere `hide()` и `destroy()` hooks могут работать не так, как ожидается, а в multi-panel plugin hooks могут срабатывать без различения конкретной панели. Cleanup нельзя строить только на этих callbacks: сохраняйте явный application state и делайте операции idempotent.

## Permissions

Permissions в UXP allow-list’ят доступ. Необъявленная permission по умолчанию запрещает соответствующую операцию. Минимизируйте scope:

- `localFileSystem` для файлов;
- `network` для сетевых доменов;
- `clipboard` для clipboard;
- `launchProcess` для внешних процессов;
- `enableAddon`/`addon` для UXP Hybrid Plugin.

`network.domains` и filesystem permissions являются частью install/runtime contract, а не просто конфигурацией UI. Изменение manifest требует повторной загрузки plugin в UDT; Watch mode не заменяет явный Unload/Load для manifest changes.

## Premiere DOM mutation boundary

Premiere DOM actions должны выполняться внутри `Project.lockedAccess()` или `Project.executeTransaction()` согласно официальному ESLint integration guidance. `create*Action()` нельзя вызывать вне lock scope, `addAction()` — вне transaction scope. Action objects не должны переживать lock scope.

Внутри `lockedAccess()`/`executeTransaction()` не следует выполнять async work. Подготовьте данные до входа в callback, выполните короткую синхронную серию action calls, затем обработайте результат снаружи. Это не общий стиль: это конкретное ограничение, которое можно ловить `@adobe/eslint-plugin-premierepro`.

```ts
const project = await app.Project.getActiveProject();
const sequence = await project.getActiveSequence();
const prepared = buildEditPlan(input);

const ok = await project.executeTransaction(
  () => {
    const action = sequence.createAddMarkerAction(prepared.time);
    project.addAction(action);
    return true;
  },
  "Apply marker plan",
);
```

Имена конкретных action factory должны сверяться с текущей API reference; пример показывает границу transaction, а не полный универсальный recipe.

## Version-specific behavior

Не переносите асинхронность ExtendScript в UXP механически. Adobe указывает, что UXP Premiere methods в основном возвращают Promises, тогда как properties designed for DOM compatibility остаются synchronous. Changelog может менять контракт: например, `Sequence.setSelection` в Premiere Pro v26.3 стал synchronous и возвращает `boolean` вместо `Promise<boolean>`.

Version guards должны быть рядом с feature call и сопровождаться fallback/error message. Нельзя определять поддержку только по наличию JavaScript property, если runtime behavior изменялся между версиями.

## Static analysis and CI

Для JS/TS projects используйте `@adobe/eslint-plugin-premierepro`. Доступны syntactic recommended rules и type-checked rules; одновременно включать обе конфигурации обычно не следует, поскольку они могут дублировать сообщения. Type-checked режим требует TypeScript, `typescript-eslint` и синхронные версии `@adobe/premierepro` typings/plugin.

Минимум CI для plugin:

1. проверить manifest schema и `host.minVersion`;
2. проверить permissions against actual imports/calls;
3. запустить ESLint с одним Premiere rule tier;
4. собрать production bundle;
5. проверить отсутствие debug/dev interfaces;
6. проверить plugin на каждой заявленной архитектуре и host version.

## Distribution boundary

Для Marketplace plugin ID должен соответствовать ID в Adobe Developer Distribution portal. UXP Hybrid Plugin должен поставлять binaries для macOS arm64, macOS x64 и Windows x64; macOS `.uxpaddon` должен быть code-signed и notarized. Это требования распространения, а не гарантия того, что native addon API одинаково ведёт себя на всех host versions.

## Known issues and caveats

- `alert()`, `confirm()` и `prompt()` в Premiere UXP пока не полностью поддерживаются.
- Lifecycle `hide()`/`destroy()` нельзя считать надёжным единственным cleanup trigger.
- UXP API version mismatch может приводить к runtime errors.
- Debug/private fields и methods не являются production API и могут привести к поломке или отклонению plugin.
- Marketplace review проверяет launch, UI, feedback, responsive behavior, platform compatibility, signing, dependencies, localization и отсутствие exposed developer tools.

## References

- [Premiere UXP overview](https://developer.adobe.com/premiere-pro/uxp/)
- [Plugin concepts](https://developer.adobe.com/premiere-pro/uxp/plugins/concepts/)
- [Manifest](https://developer.adobe.com/premiere-pro/uxp/plugins/concepts/manifest/)
- [Understanding UXP APIs](https://developer.adobe.com/premiere-pro/uxp/resources/fundamentals/apis/)
- [Premiere DOM APIs](https://developer.adobe.com/premiere-pro/uxp/resources/fundamentals/dom-apis/)
- [ESLint support](https://developer.adobe.com/premiere-pro/uxp/resources/fundamentals/eslint-support/)
- [Lifecycle hooks](https://developer.adobe.com/premiere-pro/uxp/plugins/tutorials/add-lifecycle-hooks/)
- [UXP changelog](https://developer.adobe.com/premiere-pro/uxp/changelog/)
- [Known issues](https://developer.adobe.com/premiere-pro/uxp/uxp-api/known-issues)
- [Marketplace review guidelines](https://developer.adobe.com/premiere-pro/uxp/plugins/distribution/review-guidelines/)
