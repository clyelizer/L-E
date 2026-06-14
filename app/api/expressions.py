"""Expression CRUD routes (admin)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.expression import Expression, Image
from app.models.user import User
from app.schemas.expression import (
    ExpressionCreate,
    ExpressionListResponse,
    ExpressionResponse,
    ExpressionUpdate,
    ImageResponse,
)

router = APIRouter(prefix="/api/v1/expressions", tags=["expressions"])


@router.get("", response_model=ExpressionListResponse)
async def list_expressions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    tier: int | None = Query(default=None, ge=1, le=3),
    search: str | None = Query(default=None, max_length=200),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """List expressions with pagination and filtering."""
    query = select(Expression)

    if tier is not None:
        query = query.where(Expression.tier == tier)
    if search:
        query = query.where(Expression.text.ilike(f"%{search}%"))

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(Expression.tier, Expression.text).offset(
        (page - 1) * page_size
    ).limit(page_size)

    # Load images
    query = query.options(joinedload(Expression.images))

    result = await db.execute(query)
    expressions = result.unique().scalars().all()

    items = []
    for expr in expressions:
        active_image = next((img for img in expr.images if img.is_active), None)
        items.append(ExpressionResponse(
            id=expr.id,
            text=expr.text,
            meaning=expr.meaning,
            metaphor=expr.metaphor,
            part_of_speech=expr.part_of_speech,
            difficulty=expr.difficulty,
            frequency_score=expr.frequency_score,
            example_sentence=expr.example_sentence,
            notes=expr.notes,
            source=expr.source,
            tags=expr.tags,
            tier=expr.tier,
            created_at=expr.created_at,
            updated_at=expr.updated_at,
            image_path=active_image.path if active_image else None,
        ))

    return ExpressionListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{expression_id}", response_model=ExpressionResponse)
async def get_expression(
    expression_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Get a single expression with its active image."""
    result = await db.execute(
        select(Expression)
        .options(joinedload(Expression.images))
        .where(Expression.id == expression_id)
    )
    expr = result.unique().scalar_one_or_none()
    if not expr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expression not found")

    active_image = next((img for img in expr.images if img.is_active), None)
    return ExpressionResponse(
        id=expr.id,
        text=expr.text,
        meaning=expr.meaning,
        metaphor=expr.metaphor,
        part_of_speech=expr.part_of_speech,
        difficulty=expr.difficulty,
        frequency_score=expr.frequency_score,
        example_sentence=expr.example_sentence,
        notes=expr.notes,
        source=expr.source,
        tags=expr.tags,
        tier=expr.tier,
        created_at=expr.created_at,
        updated_at=expr.updated_at,
        image_path=active_image.path if active_image else None,
    )


@router.post("", response_model=ExpressionResponse, status_code=status.HTTP_201_CREATED)
async def create_expression(
    body: ExpressionCreate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Create a new expression."""
    expr = Expression(**body.model_dump())
    db.add(expr)
    await db.flush()
    await db.refresh(expr)

    return ExpressionResponse(
        id=expr.id,
        text=expr.text,
        meaning=expr.meaning,
        metaphor=expr.metaphor,
        part_of_speech=expr.part_of_speech,
        difficulty=expr.difficulty,
        frequency_score=expr.frequency_score,
        example_sentence=expr.example_sentence,
        notes=expr.notes,
        source=expr.source,
        tags=expr.tags,
        tier=expr.tier,
        created_at=expr.created_at,
        updated_at=expr.updated_at,
    )


@router.put("/{expression_id}", response_model=ExpressionResponse)
async def update_expression(
    expression_id: str,
    body: ExpressionUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Update an expression."""
    result = await db.execute(select(Expression).where(Expression.id == expression_id))
    expr = result.scalar_one_or_none()
    if not expr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expression not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expr, field, value)
    await db.flush()
    await db.refresh(expr)
    return ExpressionResponse(
        id=expr.id,
        text=expr.text,
        meaning=expr.meaning,
        metaphor=expr.metaphor,
        part_of_speech=expr.part_of_speech,
        difficulty=expr.difficulty,
        frequency_score=expr.frequency_score,
        example_sentence=expr.example_sentence,
        notes=expr.notes,
        source=expr.source,
        tags=expr.tags,
        tier=expr.tier,
        created_at=expr.created_at,
        updated_at=expr.updated_at,
    )


@router.delete("/{expression_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expression(
    expression_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Delete an expression."""
    result = await db.execute(select(Expression).where(Expression.id == expression_id))
    expr = result.scalar_one_or_none()
    if not expr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expression not found")
    await db.delete(expr)
