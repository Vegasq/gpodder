# -*- coding: utf-8 -*-
#
# gPodder - A media aggregator and podcast client
# Copyright (c) 2005-2009 Thomas Perl and the gPodder Team
#
# gPodder is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# gPodder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import gtk
import hildon

import gpodder

_ = gpodder.gettext

from gpodder import util

from gpodder.gtkui.interface.common import BuilderWidget
from gpodder.gtkui.model import EpisodeListModel

class gPodderEpisodes(BuilderWidget):
    def new(self):
        self.channel = None
        # Workaround for Maemo bug XXX
        self.button_search_episodes_clear.set_name('HildonButton-thumb')
        appmenu = hildon.AppMenu()
        for action in (self.action_rename, \
                       self.action_play_m3u, \
                       self.action_login, \
                       self.action_unsubscribe):
            button = gtk.Button()
            action.connect_proxy(button)
            appmenu.append(button)
        for filter in (self.item_view_episodes_all, \
                       self.item_view_episodes_undeleted, \
                       self.item_view_episodes_downloaded):
            button = gtk.ToggleButton()
            filter.connect_proxy(button)
            appmenu.add_filter(button)
        appmenu.show_all()
        self.main_window.set_app_menu(appmenu)

    def on_rename_button_clicked(self, widget):
        if self.channel is None:
            return
        new_title = self.show_text_edit_dialog(_('Rename podcast'), \
                _('New name:'), self.channel.title)
        if new_title is not None and new_title != self.channel.title:
            self.channel.set_custom_title(new_title)
            self.main_window.set_title(self.channel.title)
            self.channel.save()
            self.show_message(_('Podcast renamed: %s') % new_title)
            self.update_podcast_list_model(urls=[self.channel.url])

    def on_login_button_clicked(self, widget):
        accept, auth_data = self.show_login_dialog(_('Login to %s') % \
                                                   self.channel.title, '', \
                                                   self.channel.username, \
                                                   self.channel.password)
        if accept:
            self.channel.username, self.channel.password = auth_data
            self.channel.save()

    def on_play_m3u_button_clicked(self, widget):
        if self.channel is not None:
            util.gui_open(self.channel.get_playlist_filename())

    def on_website_button_clicked(self, widget):
        if self.channel is not None:
            util.open_website(self.channel.link)

    def on_unsubscribe_button_clicked(self, widget):
        if self.show_confirmation(_('Really delete this podcast and all downloaded episodes?')):
            self.on_delete_event(widget, None)
            self.on_itemRemoveChannel_activate(widget)

    def on_episode_selected(self, treeview, path, column):
        model = treeview.get_model()
        episode = model.get_value(model.get_iter(path), \
                EpisodeListModel.C_EPISODE)
        self.show_episode_shownotes(episode)

    def on_delete_event(self, widget, event):
        self.main_window.hide()
        self.channel = None
        self.hide_episode_search()
        return True

    def show(self):
        self.main_window.set_title(self.channel.title)
        self.main_window.show()
        self.treeview.grab_focus()
