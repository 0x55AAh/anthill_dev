/**
 *
 * @param storage
 * @param key_prefix
 * @param data_format
 * @constructor
 */
function AnthillStorage(storage, key_prefix, data_format) {
    this.storage = window[storage] || window['sessionStorage'];
    this.key_prefix = key_prefix || 'anthill';
    this.data_format = data_format || 'json';
}

/**
 *
 * @param key
 * @returns {string}
 */
AnthillStorage.prototype.build_key = function (key) {
    return [this.key_prefix, key].join('_');
};

/**
 * Check if current value differs from previously saved
 * @param key
 * @param current_value
 * @returns {boolean}
 */
AnthillStorage.prototype.changed = function (key, current_value) {
    key = this.build_key(key);
    var old_value = this.storage.getItem(key);
    this.storage.setItem(key, current_value);
    return old_value !== null && old_value !== current_value;
};

/**
 *
 * @param key
 * @param current_value
 * @param data_format
 */
AnthillStorage.prototype.setItem = function (key, current_value, data_format) {
    key = this.build_key(key);
    data_format = data_format || this.data_format;
    if (data_format === 'json')
        current_value = JSON.stringify(current_value);
    this.storage.setItem(key, current_value);
};

/**
 *
 * @param key
 * @param data_format
 * @returns {*}
 */
AnthillStorage.prototype.getItem = function (key, data_format) {
    key = this.build_key(key);
    var value = this.storage.getItem(key);
    data_format = data_format || this.data_format;
    if (data_format === 'json')
        return JSON.parse(value);
    return value;
};

window.anthill_storage = new AnthillStorage();