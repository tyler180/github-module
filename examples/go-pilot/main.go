package main

import (
	"flag"
	"fmt"
	"strings"
)

func main() {
	name := flag.String("name", "Go pilot", "name to greet")
	flag.Parse()
	fmt.Println(greeting(*name))
}

func greeting(name string) string {
	name = strings.TrimSpace(name)
	if name == "" {
		name = "world"
	}
	return fmt.Sprintf("Hello, %s!", name)
}
