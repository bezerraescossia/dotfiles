local wezterm = require("wezterm")
local config = wezterm.config_builder()

config.color_scheme = "Oxocarbon Dark (Gogh)"
config.font = wezterm.font("Hack Nerd Font")
config.font_size = 15.0
config.window_background_opacity = 0.95
config.hide_tab_bar_if_only_one_tab = true
config.window_decorations = "NONE"

config.front_end = "OpenGL"
config.animation_fps = 60
config.max_fps = 60
config.cursor_blink_rate = 0

-- WSL domain only applies when wezterm itself runs on Windows; on native
-- Linux there's no WSL to talk to, so setting default_domain here would
-- make wezterm fail to start looking for a nonexistent domain.
if wezterm.target_triple:find("windows") then
	config.wsl_domains = {
		{
			name = "WSL:Ubuntu",
			distribution = "Ubuntu", -- ajuste pro nome da sua distro (wsl -l -v pra conferir)
			default_cwd = "/home/bezer",
		},
	}
	config.default_domain = "WSL:Ubuntu"
end
config.keys = {
	-- Desativa o disparo da ao de ShowDebugOverlay no CTRL+SHIFT+L
	{
		key = "L",
		mods = "CTRL|SHIFT",
		action = wezterm.action.DisableDefaultAssignment,
	},
	{
		key = "l",
		mods = "CTRL|SHIFT",
		action = wezterm.action.DisableDefaultAssignment,
	},
	-- Desativa caso alguma combinao com CTRL puro tente invocar
	{
		key = "l",
		mods = "CTRL",
		action = wezterm.action.DisableDefaultAssignment,
	},
}

-- Dim unfocused windows so the focused one is obvious at a glance.
local UNFOCUSED_FOREGROUND_TEXT_HSB = { hue = 1.0, saturation = 0.25, brightness = 0.45 }
local UNFOCUSED_WINDOW_BACKGROUND_OPACITY = 0.62

-- get_config_overrides() hands back a copy, so the current value is never the
-- same table we last stored; compare the fields instead of the identity.
local function same_text_hsb(actual, expected)
	if actual == nil or expected == nil then
		return actual == expected
	end
	return actual.hue == expected.hue
		and actual.saturation == expected.saturation
		and actual.brightness == expected.brightness
end

wezterm.on("window-focus-changed", function(window)
	local overrides = window:get_config_overrides() or {}
	local text_hsb, opacity
	if not window:is_focused() then
		text_hsb = UNFOCUSED_FOREGROUND_TEXT_HSB
		opacity = UNFOCUSED_WINDOW_BACKGROUND_OPACITY
	end
	-- Only write when one of the two values we own actually changes; a redundant
	-- set_config_overrides() call would trigger another config reload.
	if same_text_hsb(overrides.foreground_text_hsb, text_hsb) and overrides.window_background_opacity == opacity then
		return
	end
	overrides.foreground_text_hsb = text_hsb
	overrides.window_background_opacity = opacity
	window:set_config_overrides(overrides)
end)

return config
