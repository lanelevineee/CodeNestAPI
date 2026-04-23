// Rooms Module
class RoomsManager {
    constructor() {
        this.rooms = [];
        this.currentPage = 1;
        this.hasMore = true;
        this.loading = false;
    }

    async loadRooms(page = 1) {
        if (this.loading) return;
        
        this.loading = true;
        try {
            const data = await api.getRooms({ page });
            
            if (page === 1) {
                this.rooms = data.results || data;
            } else {
                this.rooms = [...this.rooms, ...(data.results || data)];
            }
            
            this.hasMore = !!data.next || (data.results && data.results.length > 0);
            this.currentPage = page;
            
            this.renderRooms();
        } catch (error) {
            app.showToast('Failed to load rooms', 'error');
            console.error('Error loading rooms:', error);
        } finally {
            this.loading = false;
        }
    }

    renderRooms() {
        const grid = document.getElementById('rooms-grid');
        
        if (!this.rooms || this.rooms.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-hashtag"></i>
                    <h3>No rooms yet</h3>
                    <p>Create your first room to get started</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = this.rooms.map(room => this.createRoomCard(room)).join('');
        
        // Add click handlers
        grid.querySelectorAll('.room-card').forEach(card => {
            card.addEventListener('click', () => {
                const roomId = card.dataset.roomId;
                this.openRoom(roomId);
            });
        });
    }

    createRoomCard(room) {
        const memberCount = room.member_count || room.members?.length || 0;
        const tags = room.tags || [];
        
        return `
            <div class="room-card" data-room-id="${room.id}">
                <div class="room-card-header">
                    <div class="room-icon">
                        <i class="fas fa-${room.is_private ? 'lock' : 'hashtag'}"></i>
                    </div>
                    <div class="room-info">
                        <h3>${this.escapeHtml(room.name)}</h3>
                        <p>${this.escapeHtml(room.description || 'No description')}</p>
                    </div>
                </div>
                <div class="room-meta">
                    <div class="room-members">
                        <i class="fas fa-users"></i>
                        <span>${memberCount} ${memberCount === 1 ? 'member' : 'members'}</span>
                    </div>
                    ${tags.length > 0 ? `
                        <div class="room-tags">
                            ${tags.slice(0, 3).map(tag => 
                                `<span class="tag">${this.escapeHtml(tag.name || tag)}</span>`
                            ).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async openRoom(roomId) {
        try {
            const room = await api.getRoom(roomId);
            
            // Check if user is a member, if not join
            const isMember = room.members?.some(m => m.id === auth.currentUser.id);
            
            if (!isMember && !room.is_private) {
                await api.joinRoom(roomId);
                app.showToast('Joined room successfully', 'success');
            }
            
            // Switch to messages view and open room chat
            app.switchView('messages');
            messages.openRoomChat(roomId, room);
        } catch (error) {
            app.showToast('Failed to open room', 'error');
            console.error('Error opening room:', error);
        }
    }

    async createRoom() {
        const name = document.getElementById('room-name').value.trim();
        const description = document.getElementById('room-description').value.trim();
        const tagsInput = document.getElementById('room-tags').value.trim();
        const isPrivate = document.getElementById('room-private').checked;

        if (!name) {
            app.showToast('Room name is required', 'error');
            return;
        }

        try {
            const btn = document.querySelector('#create-room-form button[type="submit"]');
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';

            // Parse tags
            const tags = tagsInput ? tagsInput.split(',').map(t => t.trim()).filter(t => t) : [];

            const roomData = {
                name,
                description: description || null,
                tags,
                is_private: isPrivate
            };

            await api.createRoom(roomData);
            
            app.showToast('Room created successfully', 'success');
            app.closeModal('create-room-modal');
            document.getElementById('create-room-form').reset();
            
            // Reload rooms
            await this.loadRooms(1);
        } catch (error) {
            app.showToast(error.message || 'Failed to create room', 'error');
        } finally {
            const btn = document.querySelector('#create-room-form button[type="submit"]');
            btn.disabled = false;
            btn.innerHTML = 'Create Room';
        }
    }

    async searchRooms(query) {
        try {
            const results = await api.searchRooms(query);
            this.rooms = results.results || results;
            this.renderRooms();
        } catch (error) {
            app.showToast('Search failed', 'error');
            console.error('Search error:', error);
        }
    }

    async deleteRoom(roomId) {
        if (!confirm('Are you sure you want to delete this room?')) {
            return;
        }

        try {
            await api.deleteRoom(roomId);
            app.showToast('Room deleted successfully', 'success');
            await this.loadRooms(1);
        } catch (error) {
            app.showToast('Failed to delete room', 'error');
        }
    }
}

// Create singleton instance
const rooms = new RoomsManager();
