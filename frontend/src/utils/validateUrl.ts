export function validateUrl(url: string): boolean {
    const urlPattern = new RegExp(
        '^(https?:\\/\\/)?' + // protocol
        '((([a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,})|' + // domain name and extension
        'localhost|' + // or localhost
        '\\d{1,3}(\\.\\d{1,3}){3})' + // or IPv4
        '(\\:\\d+)?(\\/[-a-zA-Z0-9%_.~+]*)*' + // port and path
        '(\\?[;&a-zA-Z0-9%_.~+=-]*)?' + // query string
        '(\\#[-a-zA-Z0-9_]*)?$',
        'i'
    );
    return urlPattern.test(url);
}
