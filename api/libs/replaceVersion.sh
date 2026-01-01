VERSION=$(git describe --tags --abbrev=0)

find ./src  -name "*.py" -type f


find ./src  -name "*.py" -type f -exec sed -i.bak "s/%%Version%%/$VERSION/g" {} \;
find ./src  -name "*.bak" -type f -exec rm {} \;