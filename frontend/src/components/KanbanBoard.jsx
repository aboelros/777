import { useState } from 'react';
import {
    DndContext,
    closestCenter,
    KeyboardSensor,
    PointerSensor,
    useSensor,
    useSensors,
    DragOverlay
} from '@dnd-kit/core';
import {
    arrayMove,
    SortableContext,
    sortableKeyboardCoordinates,
    horizontalListSortingStrategy,
    verticalListSortingStrategy,
    useSortable
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { motion } from 'framer-motion';
import { MoreHorizontal, Plus, DollarSign } from 'lucide-react';
import { useTranslation } from '../lib/translations';

export default function KanbanBoard({ stages, deals, onDealMove, onStageReorder, onAddDeal }) {
    const { t } = useTranslation();
    const [activeDeal, setActiveDeal] = useState(null);

    const sensors = useSensors(
        useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
        useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
    );

    const handleDragStart = (event) => {
        const { active } = event;
        const deal = deals.find(d => d.id === active.id);
        if (deal) setActiveDeal(deal);
    };

    const handleDragEnd = (event) => {
        setActiveDeal(null);
        const { active, over } = event;
        if (!over) return;

        const activeId = active.id;
        const overId = over.id;

        // Moving Deal
        const deal = deals.find(d => d.id === activeId);
        if (deal) {
            // Find drop target (Column or another Card)
            const overStageId = stages.find(s => s.id === overId)?.id ||
                deals.find(d => d.id === overId)?.stage_id;

            if (overStageId && deal.stage_id !== overStageId) {
                onDealMove(deal.id, overStageId);
            }
        }
    };

    return (
        <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
        >
            <div className="flex h-full overflow-x-auto gap-6 p-4">
                <SortableContext items={stages.map(s => s.id)} strategy={horizontalListSortingStrategy}>
                    {stages.map(stage => (
                        <KanbanColumn
                            key={stage.id}
                            stage={stage}
                            deals={deals.filter(d => d.stage_id === stage.id)}
                            onAddDeal={() => onAddDeal(stage.id)}
                        />
                    ))}
                </SortableContext>
            </div>

            <DragOverlay>
                {activeDeal ? <DealCard deal={activeDeal} /> : null}
            </DragOverlay>
        </DndContext>
    );
}

function KanbanColumn({ stage, deals, onAddDeal }) {
    const { setNodeRef } = useDroppable({ id: stage.id });
    const { t } = useTranslation();

    return (
        <div ref={setNodeRef} className="flex-shrink-0 w-80 flex flex-col h-full max-h-full">
            {/* Header */}
            <div
                className="flex items-center justify-between mb-4 p-3 rounded-lg bg-white/5 border-t-2"
                style={{ borderColor: stage.color || '#6366f1' }}
            >
                <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-200">{stage.name}</h3>
                    <span className="text-xs bg-white/10 px-2 py-0.5 rounded-full text-gray-400">
                        {deals.length}
                    </span>
                </div>
                <button className="text-gray-400 hover:text-white">
                    <MoreHorizontal className="w-4 h-4" />
                </button>
            </div>

            {/* Cards Area */}
            <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                <SortableContext items={deals.map(d => d.id)} strategy={verticalListSortingStrategy}>
                    {deals.map(deal => (
                        <SortableDealCard key={deal.id} deal={deal} />
                    ))}
                </SortableContext>

                <button
                    onClick={onAddDeal}
                    className="w-full py-2 flex items-center justify-center gap-2 text-sm text-gray-500 hover:text-sky-400 hover:bg-white/5 rounded-lg border border-dashed border-white/10 transition-colors"
                >
                    <Plus className="w-4 h-4" /> {t('deals.add_deal')}
                </button>
            </div>
        </div>
    );
}

import { useDroppable } from '@dnd-kit/core';

function SortableDealCard({ deal }) {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging
    } = useSortable({ id: deal.id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.4 : 1,
    };

    return (
        <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
            <DealCard deal={deal} />
        </div>
    );
}

function DealCard({ deal }) {
    const { t } = useTranslation();
    return (
        <div className="bg-dark-800 p-4 rounded-xl border border-white/5 shadow-sm hover:border-sky-500/30 group cursor-grab active:cursor-grabbing">
            <div className="flex justify-between items-start mb-2">
                <span className="text-xs text-sky-400 font-medium px-2 py-0.5 bg-sky-500/10 rounded">
                    {deal.company || t('deals.lead')}
                </span>
                <button className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-white transition-opacity">
                    <MoreHorizontal className="w-4 h-4" />
                </button>
            </div>

            <h4 className="font-semibold text-white mb-1">{deal.title}</h4>

            <div className="flex items-center justify-between mt-3 text-sm text-gray-400">
                <div className="flex items-center gap-1 text-green-400">
                    <DollarSign className="w-3 h-3" />
                    <span>{deal.value?.toLocaleString() || '0'}</span>
                </div>
                {deal.probability && (
                    <span className="text-xs bg-white/5 px-1.5 py-0.5 rounded">
                        {Math.round(deal.probability * 100)}%
                    </span>
                )}
            </div>
        </div>
    );
}
