def main_sidebar(request):
    from .ui.modules import MainSidebar
    return {
        'main_sidebar_entries': [
            MainSidebar.Entry(title='Configuration', icon_class='icon-gear'),
            MainSidebar.Entry(title='Craft', icon_class='icon-hammer'),
            MainSidebar.Entry(title='Discovery', icon_class='icon-direction'),
            MainSidebar.Entry(title='DLC', icon_class='icon-cloud-download2'),
            MainSidebar.Entry(title='Environment', icon_class='icon-cube'),
            MainSidebar.Entry(title='Events', icon_class='icon-calendar'),
            MainSidebar.Entry(title='Exec', icon_class='icon-circle-code'),
            MainSidebar.Entry(title='Game', icon_class='icon-steam'),
            MainSidebar.Entry(title='Leader board', icon_class='icon-sort-numeric-asc'),
            MainSidebar.Entry(title='Login', icon_class='icon-key'),
            MainSidebar.Entry(title='Market', icon_class='icon-basket'),
            MainSidebar.Entry(title='Messages', icon_class='icon-envelope'),
            MainSidebar.Entry(title='Profiles', icon_class='icon-user'),
            MainSidebar.Entry(title='Promo', icon_class='icon-gift'),
            MainSidebar.Entry(title='Report', icon_class='icon-flag3'),
            MainSidebar.Entry(title='Social', icon_class='icon-share3'),
            MainSidebar.Entry(title='Store', icon_class='icon-cart'),
        ]
    }
