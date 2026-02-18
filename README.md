# dogtail

**dogtail** is a GUI testing and UI automation framework written in Python. It uses Accessibility (AT-SPI) technologies to interact with desktop applications, allowing you to automate real user workflows reliably.

Dogtail scripts are standard Python programs and can be run like any other Python code.

It works especially well with:

* **behave** (BDD testing)
* **qecore** (extends behave + dogtail)

Dogtail supports both **Xorg** and **Wayland GNOME** environments.

> For Wayland usage details, see: [https://fedoramagazine.org/automation-through-accessibility/](https://fedoramagazine.org/automation-through-accessibility/)

---

## Table of Contents

* [News](#news)
* [FAQ](#faq)
* [Installation](#installation)
* [Dependencies](#dependencies)
* [Wayland Support](#wayland-support)
* [GTK4 Notes](#gtk4-notes)
* [Usage](#usage)
* [API References](#api-references)
* [Bugs & Support](#bugs--support)
* [Contributing](#contributing)

---

## News

### dogtail 2.x.y

Details: [https://gitlab.com/dogtail/dogtail/-/issues/29](https://gitlab.com/dogtail/dogtail/-/issues/29)

The project was fully refactored to:

* Clean up years of technical debt
* Improve maintainability and readability
* Prepare for future accessibility backends (e.g., AccessKit/Newton)

Rather than continuing to patch dogtail 1.x, the codebase was rebuilt to make future evolution easier and safer.

### dogtail 1.x.y

The legacy branch is still maintained as needed:

[https://gitlab.com/dogtail/dogtail/-/tree/dogtail-1.x](https://gitlab.com/dogtail/dogtail/-/tree/dogtail-1.x)

## FAQ

[https://gitlab.com/dogtail/dogtail/-/blob/master/FAQ.md](https://gitlab.com/dogtail/dogtail/-/blob/master/FAQ.md)

---

## Installation

### From GitLab (build locally)

```bash
git clone https://gitlab.com/dogtail/dogtail.git
cd dogtail
python3 -m build
sudo pip3 install dist/dogtail-2.*-py3-none-any.whl
```

### From GitLab (pip)

```bash
sudo dnf install python3-pip
sudo python3 -m pip install git+https://gitlab.com/dogtail/dogtail@master
```

### From PyPI

```bash
sudo python3 -m pip install dogtail
```

### From GitLab Package Registry

Packages are built automatically by CI:

[https://gitlab.com/dogtail/dogtail/-/packages/](https://gitlab.com/dogtail/dogtail/-/packages/)

---

## Dependencies

Core requirements:

* Python bindings for your distro (e.g., `python-apt`, `rpm-python`)
* GNOME Python libraries

Test targets typically include GNOME applications:

[https://www.gnome.org/](https://www.gnome.org/)

### Wayland-specific dependency

To run on Wayland GNOME, install **gnome-ponytail-daemon**:

[https://gitlab.gnome.org/ofourdan/gnome-ponytail-daemon](https://gitlab.gnome.org/ofourdan/gnome-ponytail-daemon)

The `gnome-ponytail-daemon` is packaged in Fedora distribution:
```
dnf install -y gnome-ponytail-daemon
dnf install -y python3-gnome-ponytail-daemon
```

Building from source:

```bash
sudo dnf install meson gcc glib2-devel
git clone https://gitlab.gnome.org/ofourdan/gnome-ponytail-daemon.git
cd gnome-ponytail-daemon
sudo meson setup build
sudo ninja -C build
sudo ninja -C build install
```

---

## Wayland Support

Wayland input automation is enabled through **gnome-ponytail-daemon**, which uses:

* Screen Cast API
* Remote Desktop API
* GNOME Shell Introspection

This allows Dogtail to:

* Connect to specific windows
* Translate local UI coordinates to global screen positions
* Simulate keyboard and mouse input reliably

### What this means in practice

Dogtail handles the complexity internally. Most test scripts run identically on:

* Xorg sessions
* Wayland GNOME sessions

On Xorg, traditional X input APIs are used automatically.

---

## GTK4 Notes

For GTK4 applications, **window shadows must be disabled** for accurate coordinate handling.

Add the following to:

```text
~/.config/gtk-4.0/gtk.css
```

```css
window, .popover, .tooltip {
    box-shadow: none;
}
```

### Why this is necessary

* Shadows introduce variable coordinate offsets
* Offsets differ per application, size, and scaling
* Disabling shadows ensures consistent automation behavior

Dogtail automatically manages known offsets using `dogtail.config.gtk4_offset`.

---

## Usage

Currently supported:

* GNOME and GTK applications
* Xorg and Wayland sessions
* Limited Qt support via qt-at-spi (not officially maintained)

### Enable accessibility

```bash
gsettings set org.gnome.desktop.interface toolkit-accessibility true
```

Restart applications (or log out/in) after enabling.

Headless environments using `dogtail-headless` or `qecore-headless` enable this automatically.

---

## API References

* [https://lazka.github.io/pgi-docs/#Atspi-2.0](https://lazka.github.io/pgi-docs/#Atspi-2.0)
* [https://docs.gtk.org/atspi2/index.html](https://docs.gtk.org/atspi2/index.html)

---

## Bugs & Support

Report issues here:

[https://gitlab.com/dogtail/dogtail/issues](https://gitlab.com/dogtail/dogtail/issues)

Project home:

[https://gitlab.com/dogtail/dogtail/](https://gitlab.com/dogtail/dogtail/)

API docs (incomplete for both versions, in progress for 2.x):

[http://fedorapeople.org/~vhumpa/dogtail/epydoc/](http://fedorapeople.org/~vhumpa/dogtail/epydoc/)

Mailing lists and IRC are deprecated — please use GitLab.

---

## Contributing

### Bug reports

* Search existing issues first
* Include steps to reproduce and environment details

### Feature ideas

* Open an issue to discuss before coding

### Code style guidelines

* Use docstrings for all public functions and methods
* Follow `snake_case` naming
* Prefer descriptive variable names
* Write full-sentence comments with proper punctuation

Your contributions are welcome! 🚀
