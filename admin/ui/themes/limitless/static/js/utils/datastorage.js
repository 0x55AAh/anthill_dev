/**
 *
 * @param storage
 * @param key_prefix
 * @param format
 * @constructor
 */
function AnthillStorage(storage, key_prefix, format) {
    this.storage = window[storage] || window['sessionStorage'];
    this.key_prefix = key_prefix || 'anthill_';
    this.format = format|| 'json';
}

/**
 *
 * @param key
 * @returns {string}
 */
AnthillStorage.prototype.get_key = function (key) {
    return this.key_prefix + key;
};

/**
 * Check if current value differs from previously saved
 * @param key
 * @param current_value
 * @returns {boolean}
 */
AnthillStorage.prototype.changed = function (key, current_value) {
    var _key = this.get_key(key);
    var old_value = this.storage.getItem(_key);
    this.storage.setItem(_key, current_value);
    return old_value !== null && old_value !== current_value;
};

/**
 *
 * @param key
 * @param current_value
 * @param format
 */
AnthillStorage.prototype.setItem = function (key, current_value, format) {
    var _key = this.get_key(key);
    var fmt = format || this.format;
    if (fmt === 'json')
        current_value = JSON.stringify(current_value);
    this.storage.setItem(_key, current_value);
};

/**
 *
 * @param key
 * @param format
 * @returns {*}
 */
AnthillStorage.prototype.getItem = function (key, format) {
    var fmt = format || this.format;
    var _key = this.get_key(key);
    var value = this.storage.getItem(_key);
    if (fmt === 'json')
        return JSON.parse(value);
    return value;
};

window.anthill_storage = new AnthillStorage();