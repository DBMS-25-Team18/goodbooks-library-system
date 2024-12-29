def search_query(title: str, authors: str, tag: str, isbn: str, page: int):
    query = ""
    extra_query = ""
    final = ""
    
    if title:
        extra_query += " b.title like %s"

    if authors:
        if extra_query:
            extra_query += " and"
        extra_query += " b.authors like %s"

    if isbn:
        if extra_query:
            extra_query += " and"
        extra_query += " b.isbn like %s"

    if tag:
        query += """WITH tag AS(
                    SELECT * FROM tags 
                    WHERE tag_name LIKE %s 
                    ORDER BY LENGTH(tag_name) ASC LIMIT 5)
                    SELECT * FROM tag AS t, books AS b ,book_tags AS bt 
                    WHERE bt.tag_id = t.tag_id and bt.goodreads_book_id = b.book_id"""
        final += f" ORDER BY bt.count DESC LIMIT 10 OFFSET {(page - 1) * 10}"
        if extra_query:
            query += " and"
    else:
        query += "SELECT * FROM books AS b where"
        final += f" ORDER BY b.average_rating DESC LIMIT 10 OFFSET {(page - 1) * 10}"

    query += extra_query
    query += final

    return query

def search_params(title: str, authors: str, tag: str, isbn: str):
    params = []
    if tag:
        params.append(f"%{tag}%")
    if title:
        params.append(f"%{title}%")
    if authors:
        params.append(f"%{authors}%")
    if isbn:
        params.append(f"%{isbn}%")

    return tuple(params)