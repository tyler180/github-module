package main

import "testing"

func TestGreeting(t *testing.T) {
	tests := []struct {
		name  string
		input string
		want  string
	}{
		{name: "named", input: "Go pilot", want: "Hello, Go pilot!"},
		{name: "empty", input: "", want: "Hello, world!"},
		{name: "whitespace", input: " \t\n", want: "Hello, world!"},
		{name: "trimmed", input: "  Tyler  ", want: "Hello, Tyler!"},
		{name: "unicode", input: "世界", want: "Hello, 世界!"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			if got := greeting(tt.input); got != tt.want {
				t.Errorf("greeting(%q) = %q; want %q", tt.input, got, tt.want)
			}
		})
	}
}
