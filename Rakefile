task :default => [:docs]

desc "Generate documentation"
task :docs do
    Dir.chdir "Example" do
        `jazzy \
            --clean \
            --author "Julian Raschke und Sebastian Ludwig GbR" \
            --author_url https://lurado.com \
            --github_url https://github.com/lurado/LLDO \
            --github-file-prefix https://github.com/lurado/LLDO/tree/master \
            --root-url https://lurado.github.io/LLDO/ \
            --output ../docs/ \
            --readme ../README.md \
            --module LLDO \
            --min-acl internal \
            --theme apple \
            --exclude LLDOSwiftHelper/AppDelegate.swift`

        `rm -rf build`
    end
end