# RelayHub v15 — pomocnik iPhone + PS5 (iSH, wersja testowa)

## Co potrafi
Ta paczka przystosowuje *istniejący* `login_once.py` do uruchamiania z terminala iSH na iPhonie. Nie zmienia payloadu PS5; wymagany jest RelayHub v15 z opcją **Import sesji mobilnej**. Po udanym logowaniu iPhone może wygenerować `relayhub-mobile-session.json` zgodny z importerem v15.

**Nie jest to gotowy ani potwierdzony klient Instagram na iOS.** iSH emuluje Linuksa x86 i pakiet `curl_cffi`, niezbędny nowszym instagrapi do logowania CAA/Bloks przez HTTP/2, może być niedostępny dla Twojej wersji Alpine. Skrypt wykrywa brak biblioteki i zatrzymuje instalację. Nie miesza repozytoriów Alpine (edge/testing), nie omija weryfikacji Instagram i nie obiecuje sukcesu. Jeśli instalator odmówi pracy, to realne ograniczenie iSH, a nie błąd wpisywanego hasła.

## 1. Przygotowanie iPhone'a
1. Z App Store zainstaluj **iSH Shell** (https://ish.app/).
2. Pobierz ZIP, otwórz aplikację **Pliki**, rozpakuj ZIP do folderu w lokalizacji **iSH** (jeśli lokalizacja iSH jest dostępna). Jeśli Pliki nie pokazują folderu iSH, użyj w iSH montowania folderu poprzez `mkdir -p /mnt/iphone && mount -t ios . /mnt/iphone`, a w selektorze wybierz folder z rozpakowaną paczką.
3. Otwórz iSH i przejdź do rozpakowanego folderu. Gdy wypakujesz go do `iSH/root`, będzie to `cd /root/RelayHub_iPhone_iSH`.
4. Zainstaluj zależności (jednorazowo):
   ```sh
   sh setup_ish.sh
   ```
5. Jeżeli zobaczysz informację, że bibliotek brakuje albo Python jest za stary: **zatrzymaj się; nie zmieniaj ręcznie repozytoriów iSH na edge**. `curl_cffi` wymaga zgodnej binarnej biblioteki i często nie ma jej dla emulowanego x86.

## 2. Zaloguj konto (tylko gdy diagnostyka jest zielona)
```sh
sh start.sh
```
Podaj login i hasło w terminalu iSH. Jeśli Instagram zaoferuje weryfikację przez WhatsApp, wpisz kod. Nie można wymusić kanału WhatsApp, jeżeli Instagram wybierze inny. Nie wpisuj hasła ani kodów do ChatGPT. Jeżeli pojawi się checkpoint, zakończ i potwierdź próbę w oficjalnej aplikacji Instagram.

## 3. Import do PS5
1. Jeśli logowanie **naprawdę** się powiedzie, skrypt tworzy `/root/relayhub-mobile-session.json` i `/root/.relayhub_instagram_device.json`.
2. Otwórz Safari, zaloguj się do WebGUI RelayHub v15 przez Tailscale. Wybierz **Instagram (nieoficjalny) → Import sesji mobilnej**.
3. Wybierz `relayhub-mobile-session.json` z lokalizacji **Pliki → iSH → root** (czasem trzeba najpierw użyć `mount -t ios` i skopiować plik do folderu widocznego w Plikach).
4. Kliknij **Sprawdź i zaimportuj sesję mobilną**. Sukces jest możliwy tylko jeśli Instagram odpowie poprawnie na próbę odczytu DM przez PS5.
5. Po zakończeniu usuń plik eksportu ze współdzielonej lokalizacji, a zachowaj plik profilu urządzenia tylko w zabezpieczonej pamięci iSH.

**Bezpieczeństwo**: eksport JSON zawiera dane sesji równoważne hasłu. Wgrywaj wyłącznie do własnego, chronionego WebGUI. Panel RelayHub używa HTTP; Tailscale szyfruje transmisję w tunelu, ale wejście na niezaufany panel może ujawnić sesję. Nie udostępniaj pliku, nie publikuj go w GitHub ani na czacie.

## Jeżeli iSH nie działa
Nie istnieje niezawodny sposób przeniesienia sesji Safari/Instagram do ELF za pomocą samego przeglądarkowego logowania (ciasteczka HttpOnly i izolacja domen). Nie wykorzystuj przypadkowych serwisów do eksportu cookies ani nie mieszaj repozytoriów Alpine. Alternatywą jest jednorazowe uruchomienie pomocnika w zgodnym środowisku Python (np. w zaufanej, chwilowej maszynie wirtualnej obsługiwanej przez iPhone'a), ale wtedy logowanie odbywa się poza iPhonem i musisz zaufać dostawcy środowiska. Sam PS5 nadal hostuje bota po imporcie.

## Stan testów
- Skrypty: testy składni powłoki i Pythona, test bezpiecznego eksportu JSON (bez sieci).
- Instalacja bibliotek na **rzeczywistym iSH/iOS**: niezweryfikowana.
- Logowanie Instagram / WhatsApp 2FA na iSH i import na PS5: niezweryfikowane.
