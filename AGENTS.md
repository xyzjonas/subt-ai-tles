# How-to

- use literal relative paths, no shell variables or command substitution in file commands

## UI/UX Design/implementation

- always consult 00-DESIGN-SYSTEM.md file whenever creating a new UI component
- always stick to semantic HTML
- style using scoped <style scoped> inside Vue components, leverage Vue for style reusability rather then CSS
- prefer plain CSS instead of SASS
- create vue components whenever there's a benefit in reusability or whenever the parent component grows too large
- prefer clean components instead of bloated ones - making use of Vue's composables whenever it makes sense